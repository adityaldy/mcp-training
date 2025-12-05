"""RAG Retriever - combines embeddings, Pinecone, and Gemini for Q&A"""

from typing import List, Dict, Any, Optional
from .embeddings import GoogleEmbeddings
from .pinecone_client import PineconeClient
from .gemini_client import GeminiClient


class RAGRetriever:
    """Retrieval Augmented Generation for LPDP Q&A"""
    
    def __init__(
        self,
        embeddings: GoogleEmbeddings | None = None,
        pinecone_client: PineconeClient | None = None,
        gemini_client: GeminiClient | None = None,
        top_k: int = 5
    ):
        """
        Initialize RAG Retriever
        
        Args:
            embeddings: GoogleEmbeddings instance
            pinecone_client: PineconeClient instance
            gemini_client: GeminiClient instance
            top_k: Number of chunks to retrieve
        """
        self.embeddings = embeddings or GoogleEmbeddings()
        self.pinecone = pinecone_client or PineconeClient()
        self.gemini = gemini_client or GeminiClient()
        self.top_k = top_k
    
    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User's question
            top_k: Number of results (overrides default)
            filter: Metadata filter for Pinecone
            
        Returns:
            List of retrieved chunks with scores and metadata
        """
        top_k = top_k or self.top_k
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Query Pinecone
        results = self.pinecone.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True
        )
        
        # Format results
        chunks = []
        for match in results.get("matches", []):
            chunk = {
                "id": match["id"],
                "score": match["score"],
                "content": match.get("metadata", {}).get("content", ""),
                "metadata": match.get("metadata", {})
            }
            chunks.append(chunk)
        
        return chunks
    
    def get_context(
        self,
        query: str,
        top_k: int | None = None,
        filter: Dict[str, Any] | None = None
    ) -> str:
        """
        Get formatted context from retrieved chunks
        
        Args:
            query: User's question
            top_k: Number of results
            filter: Metadata filter
            
        Returns:
            Formatted context string
        """
        chunks = self.retrieve(query, top_k, filter)
        
        if not chunks:
            return "Tidak ada informasi yang relevan ditemukan."
        
        # Format context with metadata
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            page = metadata.get("page_number", "?")
            section = metadata.get("section", "")
            
            header = f"[Sumber: Halaman {page}"
            if section:
                header += f", Bagian: {section}"
            header += f", Relevansi: {chunk['score']:.2f}]"
            
            context_parts.append(f"{header}\n{chunk['content']}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def query(
        self,
        question: str,
        top_k: int | None = None,
        filter: Dict[str, Any] | None = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Full RAG query: retrieve context and generate response
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            filter: Metadata filter
            include_sources: Whether to include source references
            
        Returns:
            Dict with answer, sources, and context
        """
        # Retrieve relevant chunks
        chunks = self.retrieve(question, top_k, filter)
        
        if not chunks:
            return {
                "answer": "Maaf, saya tidak menemukan informasi yang relevan dengan pertanyaan Anda dalam dokumen panduan pencairan LPDP.",
                "sources": [],
                "context": ""
            }
        
        # Build context
        context = self.get_context(question, top_k, filter)
        
        # Generate response
        answer = self.gemini.generate_response(question, context)
        
        # Extract sources
        sources = []
        if include_sources:
            for chunk in chunks:
                metadata = chunk.get("metadata", {})
                source = {
                    "page": metadata.get("page_number"),
                    "section": metadata.get("section", ""),
                    "relevance": round(chunk["score"], 3)
                }
                if source not in sources:
                    sources.append(source)
        
        return {
            "answer": answer,
            "sources": sources,
            "context": context
        }
    
    def search_by_topic(
        self,
        topic: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks related to a specific topic
        
        Args:
            topic: Topic to search for (e.g., "dana transportasi")
            top_k: Number of results
            
        Returns:
            List of relevant chunks
        """
        return self.retrieve(topic, top_k)
