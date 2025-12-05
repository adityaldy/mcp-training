"""Script untuk indexing dokumen PDF ke Pinecone"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.document import PDFLoader, TextChunker
from src.rag import GoogleEmbeddings, PineconeClient

load_dotenv()


def index_documents(pdf_path: str, namespace: str = ""):
    """
    Index PDF document to Pinecone
    
    Args:
        pdf_path: Path to PDF file
        namespace: Pinecone namespace
    """
    print(f"📄 Loading PDF: {pdf_path}")
    
    # Load PDF
    loader = PDFLoader(pdf_path)
    documents = loader.load()
    print(f"   Loaded {len(documents)} pages")
    
    # Chunk documents
    print("✂️  Chunking documents...")
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_documents(documents)
    print(f"   Created {len(chunks)} chunks")
    
    # Initialize embeddings
    print("🧠 Generating embeddings...")
    embeddings = GoogleEmbeddings()
    
    # Initialize Pinecone
    print("🌲 Connecting to Pinecone...")
    pinecone = PineconeClient()
    pinecone.create_index_if_not_exists()
    
    # Prepare vectors for upsert
    print("📤 Preparing vectors...")
    vectors = []
    
    for i, chunk in enumerate(chunks):
        # Generate embedding
        embedding = embeddings.embed_text(chunk.content)
        
        # Prepare metadata
        metadata = {
            "content": chunk.content,
            "source": chunk.metadata.get("source", ""),
            "page_number": chunk.metadata.get("page_number", 0),
            "section": chunk.metadata.get("section", ""),
            "chunk_index": chunk.metadata.get("chunk_index", i),
        }
        
        vector = {
            "id": chunk.chunk_id,
            "values": embedding,
            "metadata": metadata
        }
        vectors.append(vector)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"   Processed {i + 1}/{len(chunks)} chunks...")
    
    # Upsert to Pinecone
    print("📥 Uploading to Pinecone...")
    result = pinecone.upsert_vectors(vectors, namespace=namespace)
    print(f"   Uploaded {result['total_vectors']} vectors in {result['batches']} batches")
    
    # Verify
    stats = pinecone.describe_index_stats()
    print(f"\n✅ Indexing complete!")
    print(f"   Total vectors in index: {stats.get('total_vector_count', 'N/A')}")
    
    return result


def main():
    """Main function"""
    # Default PDF path
    default_pdf = project_root / "panduan-pencairan-awardee.pdf"
    
    # Check for docs folder
    docs_pdf = project_root / "docs" / "panduan-pencairan-awardee.pdf"
    
    if docs_pdf.exists():
        pdf_path = docs_pdf
    elif default_pdf.exists():
        pdf_path = default_pdf
    else:
        print("❌ Error: panduan-pencairan-awardee.pdf not found!")
        print("   Please place the PDF in the project root or docs/ folder")
        sys.exit(1)
    
    print("=" * 50)
    print("LPDP Document Indexing Script")
    print("=" * 50)
    
    index_documents(str(pdf_path))


if __name__ == "__main__":
    main()
