"""Pinecone Vector Database Client"""

import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()


class PineconeClient:
    """Handle Pinecone vector database operations"""
    
    def __init__(
        self,
        api_key: str | None = None,
        index_name: str | None = None,
        dimension: int = 768,
        metric: str = "cosine"
    ):
        """
        Initialize Pinecone client
        
        Args:
            api_key: Pinecone API key (optional, uses env var if not provided)
            index_name: Name of the Pinecone index
            dimension: Dimension of embedding vectors (768 for Google text-embedding-004)
            metric: Distance metric (cosine, euclidean, dotproduct)
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "lpdp-pencairan")
        self.dimension = dimension
        self.metric = metric
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
    
    def create_index_if_not_exists(self) -> None:
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"Created index: {self.index_name}")
        else:
            print(f"Index already exists: {self.index_name}")
        
        self.index = self.pc.Index(self.index_name)
    
    def get_index(self):
        """Get or connect to the Pinecone index"""
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
        return self.index
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone
        
        Args:
            vectors: List of vectors with id, values, and metadata
            namespace: Namespace for the vectors
            
        Returns:
            Upsert response
        """
        index = self.get_index()
        
        # Batch upsert (Pinecone recommends batches of 100)
        batch_size = 100
        responses = []
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            response = index.upsert(vectors=batch, namespace=namespace)
            responses.append(response)
        
        return {"batches": len(responses), "total_vectors": len(vectors)}
    
    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Dict[str, Any] | None = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Query Pinecone for similar vectors
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            namespace: Namespace to search in
            filter: Metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            Query results with matches
        """
        index = self.get_index()
        
        results = index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata
        )
        
        return results
    
    def delete_all(self, namespace: str = "") -> None:
        """
        Delete all vectors in a namespace
        
        Args:
            namespace: Namespace to delete from
        """
        index = self.get_index()
        index.delete(delete_all=True, namespace=namespace)
    
    def describe_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        index = self.get_index()
        return index.describe_index_stats()
