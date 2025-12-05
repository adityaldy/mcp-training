# Plan: MCP Server untuk FAQ Pencairan Beasiswa LPDP

## 📋 Overview

Membuat MCP (Model Context Protocol) Server menggunakan **FastMCP** yang dapat menjawab pertanyaan seputar pencairan keuangan beasiswa LPDP berdasarkan dokumen "Panduan Pencairan Awardee". Sistem akan menggunakan **RAG (Retrieval Augmented Generation)** dengan **Pinecone** sebagai vector database.

---

## 🎯 Tujuan

1. Membangun MCP Server yang dapat diintegrasikan dengan Claude Desktop atau aplikasi AI lainnya
2. Menyediakan jawaban akurat tentang pencairan beasiswa LPDP
3. Menggunakan RAG untuk meningkatkan akurasi dan relevansi jawaban
4. Deployment otomatis ke SSH server development via GitHub Actions

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Desktop │────▶│   FastMCP Server │────▶│    Pinecone     │
│   atau Client   │◀────│   (Python)       │◀────│  Vector DB      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   Google AI      │
                        │  (Gemini 2.0     │
                        │   Flash +        │
                        │   Embeddings)    │
                        └──────────────────┘
```

---

## 📁 Struktur Proyek

```
training-vibecode-mcp/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── server.py                   # FastMCP server utama
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py           # Google AI embeddings handler
│   │   ├── pinecone_client.py      # Pinecone vector store
│   │   ├── gemini_client.py        # Gemini 2.0 Flash client
│   │   └── retriever.py            # RAG retriever logic
│   ├── document/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py           # PDF document loader
│   │   └── chunker.py              # Text chunking logic
│   └── tools/
│       ├── __init__.py
│       └── lpdp_tools.py           # MCP tools untuk LPDP
├── scripts/
│   ├── index_documents.py          # Script untuk indexing PDF ke Pinecone
│   └── deploy.sh                   # Deployment script
├── tests/
│   ├── __init__.py
│   ├── test_server.py
│   ├── test_rag.py
│   └── test_tools.py
├── docs/
│   └── panduan-pencairan-awardee.pdf
├── .env.example                    # Template environment variables
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── README.md
└── plan.md
```

---

## 🔧 Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| MCP Framework | MCP SDK (official) |
| Programming Language | Python 3.11+ |
| Vector Database | Pinecone |
| LLM | Google Gemini 2.0 Flash |
| Embeddings | Google text-embedding-004 |
| PDF Processing | PyMuPDF (fitz) |
| Text Splitting | LangChain Text Splitters |
| CI/CD | GitHub Actions |
| Deployment | SSH to Development Server |

---

## 📝 Tahapan Pengembangan

### **Tahap 1: Setup Project Foundation**
- [x] Buat plan.md
- [x] Inisialisasi project dengan pyproject.toml
- [x] Setup virtual environment
- [x] Install dependencies (mcp, pinecone-client, google-generativeai, pymupdf, langchain)
- [x] Buat .env.example dan .gitignore
- [x] Setup konfigurasi dasar

### **Tahap 2: Document Processing**
- [x] Implementasi PDF loader menggunakan PyMuPDF
- [x] Implementasi text chunking dengan overlap
- [x] Buat script untuk memproses panduan-pencairan-awardee.pdf
- [x] Testing document processing

### **Tahap 3: Vector Database Setup**
- [x] Setup Pinecone account dan buat index
- [x] Implementasi Pinecone client
- [x] Implementasi Google AI embeddings (text-embedding-004)
- [x] Implementasi Gemini 2.0 Flash client
- [x] Buat script indexing untuk upload dokumen ke Pinecone
- [x] Testing vector search

### **Tahap 4: RAG Implementation**
- [x] Implementasi retriever untuk query Pinecone
- [x] Implementasi context assembly dari retrieved chunks
- [x] Setup similarity search dengan filtering
- [x] Testing RAG pipeline

### **Tahap 5: MCP Server Development**
- [x] Setup MCP server dengan official SDK
- [x] Implementasi MCP tools:
  - `tanya_pencairan_lpdp` - Tool utama untuk pertanyaan umum
  - `cari_komponen_dana` - Tool untuk mencari info komponen dana spesifik
  - `cek_batas_waktu` - Tool untuk mengecek deadline pengajuan
  - `info_dana_bulanan` - Tool untuk info living allowance
- [x] Implementasi MCP resources jika diperlukan
- [x] Testing MCP server secara lokal

### **Tahap 6: Testing & Documentation**
- [x] Unit tests untuk semua komponen
- [x] Integration tests untuk RAG + MCP
- [x] Dokumentasi README.md
- [x] Dokumentasi API dan tools

### **Tahap 7: CI/CD & Deployment**
- [x] Setup GitHub Actions workflow
- [x] Konfigurasi SSH deployment
- [x] Setup environment variables di GitHub Secrets
- [x] Testing deployment workflow
- [x] Deployment ke server development

---

## 💾 Environment Variables

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=lpdp-pencairan
PINECONE_ENVIRONMENT=us-east-1

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key

# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000

# SSH Deployment (untuk GitHub Actions)
SSH_HOST=your_server_host
SSH_USER=your_ssh_user
SSH_KEY=your_ssh_private_key
DEPLOY_PATH=/path/to/deployment
```

---

## 🛠️ Implementasi Detail

### 1. PDF Processing (`src/document/pdf_loader.py`)

```python
# Menggunakan PyMuPDF untuk extract text dari PDF
# Mempertahankan struktur dokumen (headers, sections)
# Output: List of documents dengan metadata (page number, section)
```

### 2. Text Chunking (`src/document/chunker.py`)

```python
# Chunk size: 1000 characters
# Chunk overlap: 200 characters
# Preserve paragraph boundaries
# Include metadata untuk setiap chunk
```

### 3. Pinecone Setup

```python
# Index Configuration:
# - Dimension: 768 (untuk Google text-embedding-004)
# - Metric: cosine
# - Pod type: starter (free tier)

# Metadata fields:
# - page_number: int
# - section: str
# - source: str
```

### 4. Gemini 2.0 Flash Setup

```python
# Model Configuration:
# - Model: gemini-2.0-flash
# - Temperature: 0.3 (untuk jawaban yang lebih konsisten)
# - Max output tokens: 2048
# - Safety settings: default

# Use cases:
# - Generate response berdasarkan context dari RAG
# - Summarize retrieved chunks jika terlalu panjang
```

### 5. MCP Tools Definition

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `tanya_pencairan_lpdp` | Menjawab pertanyaan umum tentang pencairan beasiswa LPDP | `pertanyaan: str` |
| `cari_komponen_dana` | Mencari informasi tentang komponen dana tertentu | `komponen: str` |
| `cek_batas_waktu` | Mengecek batas waktu pengajuan dana | `jenis_dana: str` |
| `info_dana_bulanan` | Informasi living allowance berdasarkan negara/kota | `lokasi: str` |
| `cari_dokumen_persyaratan` | Mencari dokumen yang dibutuhkan untuk pengajuan | `jenis_pengajuan: str` |

---

## 🚀 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml

name: Deploy MCP Server

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Server
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd ${{ secrets.DEPLOY_PATH }}
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart mcp-lpdp
```

---

## 📊 Contoh Pertanyaan yang Dapat Dijawab

1. **Pertanyaan Umum:**
   - "Apa saja komponen dana yang bisa diajukan ke LPDP?"
   - "Bagaimana cara mengajukan dana penelitian tesis?"
   - "Berapa besar dana publikasi jurnal internasional?"

2. **Pertanyaan Spesifik:**
   - "Berapa living allowance untuk mahasiswa di Jepang Tokyo?"
   - "Apa syarat pengajuan dana seminar internasional?"
   - "Kapan batas akhir pengajuan dana transportasi kepulangan?"

3. **Pertanyaan Prosedural:**
   - "Dokumen apa saja yang diperlukan untuk pengajuan visa?"
   - "Bagaimana mekanisme pencairan dana hidup bulanan?"
   - "Apa yang harus dilakukan jika rekening luar negeri belum valid?"

---

## 🔐 Security Considerations

1. **API Keys**: Semua API keys disimpan di environment variables dan GitHub Secrets
2. **SSH Access**: Menggunakan SSH key-based authentication
3. **Pinecone**: Menggunakan namespace terpisah untuk development dan production
4. **Rate Limiting**: Implementasi rate limiting untuk prevent abuse

---

## 📈 Monitoring & Maintenance

1. **Logging**: Implementasi structured logging untuk debugging
2. **Health Check**: Endpoint untuk monitoring server status
3. **Document Update**: Prosedur untuk update dokumen dan re-indexing

---

## ⏱️ Timeline Estimasi

| Tahap | Durasi Estimasi |
|-------|-----------------|
| Setup Project | 2 jam |
| Document Processing | 3 jam |
| Vector Database | 3 jam |
| RAG Implementation | 4 jam |
| MCP Server | 4 jam |
| Testing | 3 jam |
| CI/CD & Deployment | 3 jam |
| **Total** | **~22 jam** |

---

## ✅ Checklist Approval

Sebelum memulai coding, mohon review dan approve:

- [ ] Struktur proyek sudah sesuai
- [ ] Tech stack sudah sesuai kebutuhan
- [ ] MCP tools yang didefinisikan sudah mencakup kebutuhan
- [ ] Workflow deployment sudah sesuai
- [ ] Timeline estimasi reasonable

---

## 📝 Notes

- Pinecone free tier memiliki limit 100K vectors, cukup untuk dokumen panduan pencairan
- Google text-embedding-004 dipilih karena:
  - Gratis dengan quota generous (1500 requests/min)
  - Dimension 768 lebih efisien untuk storage di Pinecone
  - Performa sangat baik untuk bahasa Indonesia
- Gemini 2.0 Flash dipilih karena:
  - Response time sangat cepat (~200ms)
  - Context window 1M tokens
  - Gratis dengan quota generous
  - Mendukung bahasa Indonesia dengan baik
- FastMCP dipilih karena lebih mudah digunakan dibanding MCP SDK standar
- Dokumen akan di-chunk dengan overlap untuk memastikan konteks tidak terpotong

---

**Silakan review plan ini dan beri approval untuk memulai implementasi.** 🚀
