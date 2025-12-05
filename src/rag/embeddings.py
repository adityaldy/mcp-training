"""Google AI Embeddings using text-embedding-004"""

import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GoogleEmbeddings:
    """Handle text embeddings using Google AI text-embedding-004"""
    
    MODEL_NAME = "models/text-embedding-004"
    DIMENSION = 768  # text-embedding-004 produces 768-dimensional vectors
    
    def __init__(self, api_key: str | None = None):
        """
        Initialize Google Embeddings client
        
        Args:
            api_key: Google AI API key (optional, uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        result = genai.embed_content(
            model=self.MODEL_NAME,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        result = genai.embed_content(
            model=self.MODEL_NAME,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Get the dimension of embedding vectors"""
        return self.DIMENSION
