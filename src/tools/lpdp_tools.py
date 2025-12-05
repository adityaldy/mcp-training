"""LPDP MCP Tools - Tools untuk menjawab pertanyaan tentang pencairan beasiswa"""

from typing import Dict, Any, Optional
from ..rag import RAGRetriever


class LPDPTools:
    """Collection of tools for LPDP scholarship disbursement queries"""
    
    def __init__(self, retriever: RAGRetriever | None = None):
        """
        Initialize LPDP Tools
        
        Args:
            retriever: RAGRetriever instance
        """
        self.retriever = retriever or RAGRetriever()
    
    def tanya_pencairan_lpdp(self, pertanyaan: str) -> Dict[str, Any]:
        """
        Menjawab pertanyaan umum tentang pencairan beasiswa LPDP
        
        Args:
            pertanyaan: Pertanyaan pengguna tentang pencairan beasiswa
            
        Returns:
            Dict dengan jawaban dan sumber referensi
        """
        result = self.retriever.query(pertanyaan, top_k=5)
        
        return {
            "jawaban": result["answer"],
            "sumber": result["sources"]
        }
    
    def cari_komponen_dana(self, komponen: str) -> Dict[str, Any]:
        """
        Mencari informasi tentang komponen dana tertentu
        
        Args:
            komponen: Nama komponen dana (misal: "dana penelitian", "SPP", "asuransi")
            
        Returns:
            Dict dengan informasi komponen dana
        """
        query = f"Jelaskan tentang {komponen} beasiswa LPDP, termasuk besaran, syarat, dan cara pengajuan"
        result = self.retriever.query(query, top_k=7)
        
        return {
            "komponen": komponen,
            "informasi": result["answer"],
            "sumber": result["sources"]
        }
    
    def cek_batas_waktu(self, jenis_dana: str) -> Dict[str, Any]:
        """
        Mengecek batas waktu pengajuan dana
        
        Args:
            jenis_dana: Jenis dana yang ingin dicek (misal: "transportasi", "penelitian")
            
        Returns:
            Dict dengan informasi batas waktu
        """
        query = f"Kapan batas waktu atau deadline pengajuan {jenis_dana} LPDP?"
        result = self.retriever.query(query, top_k=5)
        
        return {
            "jenis_dana": jenis_dana,
            "batas_waktu": result["answer"],
            "sumber": result["sources"]
        }
    
    def info_dana_bulanan(self, lokasi: str) -> Dict[str, Any]:
        """
        Informasi living allowance berdasarkan negara/kota
        
        Args:
            lokasi: Nama negara atau kota (misal: "Jepang", "Tokyo", "Australia")
            
        Returns:
            Dict dengan informasi living allowance
        """
        query = f"Berapa living allowance atau dana hidup bulanan untuk mahasiswa LPDP di {lokasi}?"
        result = self.retriever.query(query, top_k=5)
        
        return {
            "lokasi": lokasi,
            "informasi_dana_bulanan": result["answer"],
            "sumber": result["sources"]
        }
    
    def cari_dokumen_persyaratan(self, jenis_pengajuan: str) -> Dict[str, Any]:
        """
        Mencari dokumen yang dibutuhkan untuk pengajuan
        
        Args:
            jenis_pengajuan: Jenis pengajuan (misal: "visa", "transportasi", "penelitian")
            
        Returns:
            Dict dengan daftar dokumen yang diperlukan
        """
        query = f"Dokumen apa saja yang diperlukan untuk pengajuan {jenis_pengajuan} LPDP?"
        result = self.retriever.query(query, top_k=5)
        
        return {
            "jenis_pengajuan": jenis_pengajuan,
            "dokumen_persyaratan": result["answer"],
            "sumber": result["sources"]
        }
