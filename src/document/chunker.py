"""Text Chunker for splitting documents into smaller chunks"""

from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    """Represents a text chunk with content and metadata"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str


class TextChunker:
    """Split documents into smaller chunks for embedding"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] | None = None
    ):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
            separators: List of separators to use for splitting
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=len,
        )
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] | None = None) -> List[Chunk]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            metadata: Base metadata to include in each chunk
            
        Returns:
            List of Chunk objects
        """
        metadata = metadata or {}
        chunks = []
        
        # Split text
        split_texts = self.splitter.split_text(text)
        
        for i, chunk_text in enumerate(split_texts):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(split_texts),
            }
            
            # Generate chunk ID
            source = metadata.get("source", "unknown")
            page = metadata.get("page_number", 0)
            chunk_id = f"{source}_p{page}_c{i}"
            
            chunk = Chunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_id
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_documents(self, documents: List[Any]) -> List[Chunk]:
        """
        Split multiple documents into chunks
        
        Args:
            documents: List of Document objects (with content and metadata attributes)
            
        Returns:
            List of Chunk objects
        """
        all_chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_text(doc.content, doc.metadata)
            all_chunks.extend(doc_chunks)
        
        # Update chunk IDs with global index
        for i, chunk in enumerate(all_chunks):
            chunk.metadata["global_chunk_index"] = i
        
        return all_chunks


def chunk_documents(
    documents: List[Any],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Chunk]:
    """
    Convenience function to chunk documents
    
    Args:
        documents: List of Document objects
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of Chunk objects
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_documents(documents)
