"""PDF Loader using PyMuPDF"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document chunk with content and metadata"""
    content: str
    metadata: Dict[str, Any]


class PDFLoader:
    """Load and extract text from PDF documents"""
    
    def __init__(self, file_path: str | Path):
        """
        Initialize PDF loader
        
        Args:
            file_path: Path to the PDF file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        if not self.file_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {file_path}")
    
    def load(self) -> List[Document]:
        """
        Load PDF and extract text from each page
        
        Returns:
            List of Document objects with page content and metadata
        """
        documents = []
        
        with fitz.open(self.file_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Skip empty pages
                if not text.strip():
                    continue
                
                # Clean text
                text = self._clean_text(text)
                
                # Extract section title if present
                section = self._extract_section(text)
                
                document = Document(
                    content=text,
                    metadata={
                        "source": str(self.file_path.name),
                        "page_number": page_num + 1,
                        "section": section,
                        "total_pages": len(doc)
                    }
                )
                documents.append(document)
        
        return documents
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_section(self, text: str) -> str:
        """
        Extract section title from text
        
        Args:
            text: Page text content
            
        Returns:
            Section title or empty string
        """
        # Common section patterns in LPDP document
        section_keywords = [
            "Dana Pendaftaran",
            "Dana SPP",
            "Dana Tunjangan Buku",
            "Dana Bantuan Penelitian",
            "Dana Bantuan Seminar",
            "Dana Bantuan Publikasi",
            "Dana Transportasi",
            "Dana Aplikasi Visa",
            "Dana Asuransi Kesehatan",
            "Dana Hidup Bulanan",
            "Dana Kedatangan",
            "Dana Tunjangan Keluarga",
            "Insentif Kelulusan",
            "Dana Keadaan Darurat",
            "Dana Pelatihan",
            "Dana Lomba Internasional",
            "Dana Pendamping Disabilitas",
        ]
        
        first_lines = text[:500].lower()
        
        for keyword in section_keywords:
            if keyword.lower() in first_lines:
                return keyword
        
        return ""
    
    def get_full_text(self) -> str:
        """
        Get full text from all pages
        
        Returns:
            Concatenated text from all pages
        """
        documents = self.load()
        return "\n\n".join([doc.content for doc in documents])


def load_pdf(file_path: str | Path) -> List[Document]:
    """
    Convenience function to load a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects
    """
    loader = PDFLoader(file_path)
    return loader.load()
