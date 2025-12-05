# LPDP MCP Server

MCP Server untuk menjawab pertanyaan seputar pencairan keuangan beasiswa LPDP menggunakan RAG (Retrieval Augmented Generation) dengan Pinecone dan Gemini 2.0 Flash.

## 🚀 Fitur

- **RAG-powered Q&A**: Menjawab pertanyaan berdasarkan dokumen Panduan Pencairan Awardee LPDP
- **Vector Search**: Menggunakan Pinecone untuk pencarian semantik yang akurat
- **Gemini 2.0 Flash**: Response cepat dengan dukungan bahasa Indonesia yang baik
- **MCP Protocol**: Dapat diintegrasikan dengan Claude Desktop dan aplikasi AI lainnya

## 📋 Prerequisites

- Python 3.10+ (wajib untuk MCP SDK)
- Pinecone account (free tier)
- Google AI API key

## 🛠️ Instalasi

1. Clone repository:
```bash
git clone <repository-url>
cd training-vibecode-mcp
```

2. Install Python 3.11 (jika belum ada):
```bash
# macOS dengan Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv
```

3. Buat virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
.\venv\Scripts\activate  # Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Setup environment variables:
```bash
cp .env.example .env
# Edit .env dengan API keys Anda
```

## 📚 Indexing Dokumen

Sebelum menggunakan server, index dokumen PDF ke Pinecone:

```bash
python -m scripts.index_documents
```

## 🖥️ Menjalankan Server

### Sebagai MCP Server (untuk Claude Desktop)

Tambahkan konfigurasi berikut ke `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lpdp-pencairan": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/training-vibecode-mcp",
      "env": {
        "PINECONE_API_KEY": "your_key",
        "GOOGLE_API_KEY": "your_key"
      }
    }
  }
}
```

### Standalone Mode

```bash
python -m src.server
```

## 🔧 MCP Tools

| Tool | Deskripsi |
|------|-----------|
| `tanya_pencairan_lpdp` | Menjawab pertanyaan umum tentang pencairan beasiswa |
| `cari_komponen_dana` | Mencari informasi komponen dana spesifik |
| `cek_batas_waktu` | Mengecek deadline pengajuan dana |
| `info_dana_bulanan` | Informasi living allowance per negara/kota |
| `cari_dokumen_persyaratan` | Dokumen yang dibutuhkan untuk pengajuan |

## 📊 Contoh Penggunaan

```
User: Berapa living allowance untuk mahasiswa di Jepang?
Bot: Living allowance untuk mahasiswa LPDP di Jepang adalah:
     - Tokyo: JPY 195,000/bulan
     - Kota lain: JPY 170,000/bulan
```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT License
