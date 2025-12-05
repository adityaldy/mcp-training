"""MCP Server for LPDP FAQ using official MCP SDK"""

import asyncio
import os
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

from .rag import RAGRetriever
from .tools import LPDPTools

# Load environment variables
load_dotenv()

# Initialize MCP server
server = Server("lpdp-pencairan-faq")

# Lazy-loaded instances
_retriever = None
_tools = None


def get_retriever() -> RAGRetriever:
    """Get or create RAG retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever


def get_tools() -> LPDPTools:
    """Get or create LPDP tools instance"""
    global _tools
    if _tools is None:
        _tools = LPDPTools(retriever=get_retriever())
    return _tools


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="tanya_pencairan_lpdp",
            description="""Menjawab pertanyaan umum tentang pencairan beasiswa LPDP.
            
Gunakan tool ini untuk pertanyaan umum seputar pencairan dana beasiswa LPDP,
termasuk prosedur, syarat, dan ketentuan pencairan.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "pertanyaan": {
                        "type": "string",
                        "description": "Pertanyaan tentang pencairan beasiswa LPDP"
                    }
                },
                "required": ["pertanyaan"]
            }
        ),
        Tool(
            name="cari_komponen_dana",
            description="""Mencari informasi tentang komponen dana tertentu dalam beasiswa LPDP.
            
Komponen dana meliputi: Dana SPP, Dana Penelitian, Dana Seminar, Dana Publikasi,
Dana Transportasi, Dana Asuransi, Dana Kedatangan, dll.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "komponen": {
                        "type": "string",
                        "description": "Nama komponen dana (misal: 'dana penelitian', 'SPP')"
                    }
                },
                "required": ["komponen"]
            }
        ),
        Tool(
            name="cek_batas_waktu",
            description="""Mengecek batas waktu pengajuan dana beasiswa LPDP.
            
Dapat mengecek deadline untuk berbagai jenis dana seperti transportasi,
penelitian, seminar, publikasi, visa, asuransi, dll.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "jenis_dana": {
                        "type": "string",
                        "description": "Jenis dana yang ingin dicek batas waktunya"
                    }
                },
                "required": ["jenis_dana"]
            }
        ),
        Tool(
            name="info_dana_bulanan",
            description="""Informasi living allowance (dana hidup bulanan) berdasarkan negara atau kota.
            
Dapat memasukkan nama negara (Jepang, Australia, Inggris) atau
nama kota (Tokyo, London, Sydney).""",
            inputSchema={
                "type": "object",
                "properties": {
                    "lokasi": {
                        "type": "string",
                        "description": "Nama negara atau kota tujuan studi"
                    }
                },
                "required": ["lokasi"]
            }
        ),
        Tool(
            name="cari_dokumen_persyaratan",
            description="""Mencari dokumen yang dibutuhkan untuk pengajuan dana LPDP.
            
Dapat mencari persyaratan untuk pengajuan visa, transportasi,
dana penelitian, seminar internasional, dll.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "jenis_pengajuan": {
                        "type": "string",
                        "description": "Jenis pengajuan yang ingin diketahui persyaratannya"
                    }
                },
                "required": ["jenis_pengajuan"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    tools = get_tools()
    
    if name == "tanya_pencairan_lpdp":
        result = tools.tanya_pencairan_lpdp(arguments["pertanyaan"])
        response = result["jawaban"]
        if result.get("sumber"):
            response += "\n\n📚 Sumber:"
            for src in result["sumber"][:3]:
                response += f"\n- Halaman {src['page']}"
                if src.get('section'):
                    response += f" ({src['section']})"
        return [TextContent(type="text", text=response)]
    
    elif name == "cari_komponen_dana":
        result = tools.cari_komponen_dana(arguments["komponen"])
        response = f"📋 Informasi {result['komponen'].title()}\n\n"
        response += result["informasi"]
        if result.get("sumber"):
            response += "\n\n📚 Sumber:"
            for src in result["sumber"][:3]:
                response += f"\n- Halaman {src['page']}"
                if src.get('section'):
                    response += f" ({src['section']})"
        return [TextContent(type="text", text=response)]
    
    elif name == "cek_batas_waktu":
        result = tools.cek_batas_waktu(arguments["jenis_dana"])
        response = f"⏰ Batas Waktu Pengajuan {result['jenis_dana'].title()}\n\n"
        response += result["batas_waktu"]
        if result.get("sumber"):
            response += "\n\n📚 Sumber:"
            for src in result["sumber"][:3]:
                response += f"\n- Halaman {src['page']}"
        return [TextContent(type="text", text=response)]
    
    elif name == "info_dana_bulanan":
        result = tools.info_dana_bulanan(arguments["lokasi"])
        response = f"💰 Dana Hidup Bulanan di {result['lokasi'].title()}\n\n"
        response += result["informasi_dana_bulanan"]
        if result.get("sumber"):
            response += "\n\n📚 Sumber:"
            for src in result["sumber"][:3]:
                response += f"\n- Halaman {src['page']}"
        return [TextContent(type="text", text=response)]
    
    elif name == "cari_dokumen_persyaratan":
        result = tools.cari_dokumen_persyaratan(arguments["jenis_pengajuan"])
        response = f"📄 Dokumen Persyaratan untuk {result['jenis_pengajuan'].title()}\n\n"
        response += result["dokumen_persyaratan"]
        if result.get("sumber"):
            response += "\n\n📚 Sumber:"
            for src in result["sumber"][:3]:
                response += f"\n- Halaman {src['page']}"
        return [TextContent(type="text", text=response)]
    
    else:
        return [TextContent(type="text", text=f"Tool '{name}' tidak ditemukan")]


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="lpdp://info",
            name="Server Info",
            description="Informasi tentang LPDP MCP Server",
            mimeType="text/plain"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "lpdp://info":
        return """
# LPDP Pencairan FAQ Server

Server MCP ini menyediakan informasi tentang pencairan beasiswa LPDP berdasarkan 
dokumen "Panduan Pencairan Awardee" yang berlaku sejak 29 Oktober 2025.

## Tools yang tersedia:

1. **tanya_pencairan_lpdp** - Pertanyaan umum tentang pencairan
2. **cari_komponen_dana** - Informasi komponen dana spesifik
3. **cek_batas_waktu** - Deadline pengajuan dana
4. **info_dana_bulanan** - Living allowance per lokasi
5. **cari_dokumen_persyaratan** - Dokumen yang dibutuhkan

## Contoh pertanyaan:
- "Bagaimana cara mengajukan dana penelitian tesis?"
- "Berapa living allowance di Jepang?"
- "Kapan batas waktu pengajuan dana transportasi?"
"""
    return f"Resource tidak ditemukan: {uri}"


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
