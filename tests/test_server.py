"""Tests for MCP server and tools"""

import pytest
from unittest.mock import Mock, patch


class TestLPDPTools:
    """Tests for LPDPTools class"""
    
    def test_tanya_pencairan_lpdp(self):
        """Test tanya_pencairan_lpdp tool"""
        from src.tools.lpdp_tools import LPDPTools
        
        # Mock retriever
        mock_retriever = Mock()
        mock_retriever.query.return_value = {
            "answer": "Dana transportasi diberikan untuk perjalanan dari kota asal ke kota tujuan studi.",
            "sources": [{"page": 19, "section": "Dana Transportasi", "relevance": 0.95}],
            "context": "test context"
        }
        
        tools = LPDPTools(retriever=mock_retriever)
        result = tools.tanya_pencairan_lpdp("Bagaimana ketentuan dana transportasi?")
        
        assert "jawaban" in result
        assert "sumber" in result
        assert "Dana transportasi" in result["jawaban"]
    
    def test_cari_komponen_dana(self):
        """Test cari_komponen_dana tool"""
        from src.tools.lpdp_tools import LPDPTools
        
        mock_retriever = Mock()
        mock_retriever.query.return_value = {
            "answer": "Dana penelitian tesis maksimal Rp 25.000.000 untuk yang menggunakan laboratorium.",
            "sources": [{"page": 10, "section": "Dana Bantuan Penelitian", "relevance": 0.92}],
            "context": "test context"
        }
        
        tools = LPDPTools(retriever=mock_retriever)
        result = tools.cari_komponen_dana("dana penelitian")
        
        assert "komponen" in result
        assert "informasi" in result
        assert result["komponen"] == "dana penelitian"
    
    def test_cek_batas_waktu(self):
        """Test cek_batas_waktu tool"""
        from src.tools.lpdp_tools import LPDPTools
        
        mock_retriever = Mock()
        mock_retriever.query.return_value = {
            "answer": "Batas akhir pengajuan dana transportasi adalah 4 bulan setelah sampai di tujuan.",
            "sources": [{"page": 21, "section": "Dana Transportasi", "relevance": 0.90}],
            "context": "test context"
        }
        
        tools = LPDPTools(retriever=mock_retriever)
        result = tools.cek_batas_waktu("transportasi")
        
        assert "jenis_dana" in result
        assert "batas_waktu" in result
        assert "4 bulan" in result["batas_waktu"]
    
    def test_info_dana_bulanan(self):
        """Test info_dana_bulanan tool"""
        from src.tools.lpdp_tools import LPDPTools
        
        mock_retriever = Mock()
        mock_retriever.query.return_value = {
            "answer": "Living allowance di Jepang Tokyo adalah JPY 195,000 per bulan.",
            "sources": [{"page": 54, "section": "Dana Hidup Bulanan", "relevance": 0.98}],
            "context": "test context"
        }
        
        tools = LPDPTools(retriever=mock_retriever)
        result = tools.info_dana_bulanan("Jepang")
        
        assert "lokasi" in result
        assert "informasi_dana_bulanan" in result
        assert "JPY 195,000" in result["informasi_dana_bulanan"]
    
    def test_cari_dokumen_persyaratan(self):
        """Test cari_dokumen_persyaratan tool"""
        from src.tools.lpdp_tools import LPDPTools
        
        mock_retriever = Mock()
        mock_retriever.query.return_value = {
            "answer": "Dokumen untuk visa: Invoice biaya pengurusan visa, bukti pembayaran.",
            "sources": [{"page": 23, "section": "Dana Aplikasi Visa", "relevance": 0.89}],
            "context": "test context"
        }
        
        tools = LPDPTools(retriever=mock_retriever)
        result = tools.cari_dokumen_persyaratan("visa")
        
        assert "jenis_pengajuan" in result
        assert "dokumen_persyaratan" in result
        assert "Invoice" in result["dokumen_persyaratan"]
