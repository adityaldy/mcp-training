"""Tests for document processing components"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestPDFLoader:
    """Tests for PDFLoader class"""
    
    def test_load_raises_on_missing_file(self):
        """Test that FileNotFoundError is raised for missing files"""
        from src.document.pdf_loader import PDFLoader
        
        with pytest.raises(FileNotFoundError):
            PDFLoader("/nonexistent/path/file.pdf")
    
    def test_load_raises_on_non_pdf(self, tmp_path):
        """Test that ValueError is raised for non-PDF files"""
        from src.document.pdf_loader import PDFLoader
        
        # Create a non-PDF file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("test content")
        
        with pytest.raises(ValueError):
            PDFLoader(txt_file)
    
    @patch('src.document.pdf_loader.fitz')
    def test_load_extracts_text(self, mock_fitz, tmp_path):
        """Test that PDF text is extracted correctly"""
        from src.document.pdf_loader import PDFLoader
        
        # Create a dummy PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")
        
        # Mock fitz document
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content from page 1"
        
        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__len__ = MagicMock(return_value=1)
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)
        
        mock_fitz.open.return_value = mock_doc
        
        loader = PDFLoader(pdf_file)
        documents = loader.load()
        
        assert len(documents) == 1
        assert "Test content from page 1" in documents[0].content
        assert documents[0].metadata["page_number"] == 1


class TestTextChunker:
    """Tests for TextChunker class"""
    
    def test_chunk_text_creates_chunks(self):
        """Test that text is split into chunks"""
        from src.document.chunker import TextChunker
        
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        # Create text longer than chunk size
        text = "Lorem ipsum dolor sit amet. " * 20
        
        chunks = chunker.chunk_text(text, {"source": "test.pdf"})
        
        assert len(chunks) > 1
        assert all(len(c.content) <= 100 + 50 for c in chunks)  # Allow some flexibility
    
    def test_chunk_preserves_metadata(self):
        """Test that metadata is preserved in chunks"""
        from src.document.chunker import TextChunker
        
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        text = "Short text for testing."
        metadata = {"source": "test.pdf", "page_number": 5}
        
        chunks = chunker.chunk_text(text, metadata)
        
        assert len(chunks) >= 1
        assert chunks[0].metadata["source"] == "test.pdf"
        assert chunks[0].metadata["page_number"] == 5
    
    def test_chunk_documents(self):
        """Test chunking multiple documents"""
        from src.document.chunker import TextChunker
        from src.document.pdf_loader import Document
        
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        documents = [
            Document(content="Document one content. " * 10, metadata={"page_number": 1}),
            Document(content="Document two content. " * 10, metadata={"page_number": 2})
        ]
        
        chunks = chunker.chunk_documents(documents)
        
        assert len(chunks) >= 2
        # Check that global chunk indices are assigned
        assert all("global_chunk_index" in c.metadata for c in chunks)
