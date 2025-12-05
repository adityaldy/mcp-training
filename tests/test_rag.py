"""Tests for RAG components"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGoogleEmbeddings:
    """Tests for GoogleEmbeddings class"""
    
    @patch('src.rag.embeddings.genai')
    def test_embed_text(self, mock_genai):
        """Test embedding generation for text"""
        from src.rag.embeddings import GoogleEmbeddings
        
        # Mock the embedding response
        mock_genai.embed_content.return_value = {
            'embedding': [0.1] * 768
        }
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            embeddings = GoogleEmbeddings()
            result = embeddings.embed_text("Test text")
        
        assert len(result) == 768
        assert all(isinstance(x, float) for x in result)
    
    @patch('src.rag.embeddings.genai')
    def test_embed_query(self, mock_genai):
        """Test embedding generation for query"""
        from src.rag.embeddings import GoogleEmbeddings
        
        mock_genai.embed_content.return_value = {
            'embedding': [0.2] * 768
        }
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            embeddings = GoogleEmbeddings()
            result = embeddings.embed_query("Test query")
        
        assert len(result) == 768
    
    def test_dimension_property(self):
        """Test that dimension property returns correct value"""
        from src.rag.embeddings import GoogleEmbeddings
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            with patch('src.rag.embeddings.genai'):
                embeddings = GoogleEmbeddings()
                assert embeddings.dimension == 768


class TestGeminiClient:
    """Tests for GeminiClient class"""
    
    @patch('src.rag.gemini_client.genai')
    def test_generate_response(self, mock_genai):
        """Test response generation"""
        from src.rag.gemini_client import GeminiClient
        
        # Mock the model and response
        mock_model = MagicMock()
        mock_model.generate_content.return_value = MagicMock(text="Test response")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            client = GeminiClient()
            result = client.generate_response(
                query="Test question",
                context="Test context"
            )
        
        assert result == "Test response"


class TestRAGRetriever:
    """Tests for RAGRetriever class"""
    
    def test_retrieve_returns_chunks(self):
        """Test that retrieve returns formatted chunks"""
        from src.rag.retriever import RAGRetriever
        
        # Mock dependencies
        mock_embeddings = Mock()
        mock_embeddings.embed_query.return_value = [0.1] * 768
        
        mock_pinecone = Mock()
        mock_pinecone.query.return_value = {
            "matches": [
                {
                    "id": "chunk_1",
                    "score": 0.95,
                    "metadata": {
                        "content": "Test content",
                        "page_number": 1,
                        "section": "Test Section"
                    }
                }
            ]
        }
        
        mock_gemini = Mock()
        
        retriever = RAGRetriever(
            embeddings=mock_embeddings,
            pinecone_client=mock_pinecone,
            gemini_client=mock_gemini
        )
        
        result = retriever.retrieve("test query")
        
        assert len(result) == 1
        assert result[0]["id"] == "chunk_1"
        assert result[0]["score"] == 0.95
        assert result[0]["content"] == "Test content"
    
    def test_query_returns_answer(self):
        """Test that query returns formatted answer"""
        from src.rag.retriever import RAGRetriever
        
        # Mock dependencies
        mock_embeddings = Mock()
        mock_embeddings.embed_query.return_value = [0.1] * 768
        
        mock_pinecone = Mock()
        mock_pinecone.query.return_value = {
            "matches": [
                {
                    "id": "chunk_1",
                    "score": 0.95,
                    "metadata": {
                        "content": "Living allowance di Jepang adalah JPY 195,000",
                        "page_number": 54,
                        "section": "Dana Hidup Bulanan"
                    }
                }
            ]
        }
        
        mock_gemini = Mock()
        mock_gemini.generate_response.return_value = "Living allowance di Jepang Tokyo adalah JPY 195,000 per bulan."
        
        retriever = RAGRetriever(
            embeddings=mock_embeddings,
            pinecone_client=mock_pinecone,
            gemini_client=mock_gemini
        )
        
        result = retriever.query("Berapa living allowance di Jepang?")
        
        assert "answer" in result
        assert "sources" in result
        assert "JPY 195,000" in result["answer"]
