"""Gemini 2.0 Flash Client for generating responses"""

import os
import time
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Handle text generation using Gemini 2.0 Flash"""
    
    MODEL_NAME = "models/gemini-2.0-flash"
    REQUESTS_PER_MINUTE = 5  # Rate limit: 5 requests per minute
    
    # Class-level rate limiting state
    _last_request_time: float = 0
    _request_interval: float = 60.0 / REQUESTS_PER_MINUTE  # 12 seconds between requests
    
    def __init__(
        self,
        api_key: str | None = None,
        temperature: float = 0.3,
        max_output_tokens: int = 2048
    ):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google AI API key (optional, uses env var if not provided)
            temperature: Temperature for response generation (0-1)
            max_output_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        self.generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        
        self.model = genai.GenerativeModel(
            model_name=self.MODEL_NAME,
            generation_config=self.generation_config
        )
    
    def generate_response(
        self,
        query: str,
        context: str,
        system_prompt: str | None = None
    ) -> str:
        """
        Generate response based on query and context
        
        Args:
            query: User's question
            context: Retrieved context from RAG
            system_prompt: Optional system prompt
            
        Returns:
            Generated response text
        """
        default_system_prompt = """Anda adalah asisten AI yang membantu menjawab pertanyaan tentang pencairan beasiswa LPDP (Lembaga Pengelola Dana Pendidikan).

Gunakan HANYA informasi dari konteks yang diberikan untuk menjawab pertanyaan.
Jika informasi tidak tersedia dalam konteks, katakan bahwa Anda tidak menemukan informasi tersebut.
Jawab dalam Bahasa Indonesia dengan jelas dan terstruktur.
Sertakan referensi ke bagian dokumen jika relevan."""

        system_prompt = system_prompt or default_system_prompt
        
        prompt = f"""{system_prompt}

KONTEKS:
{context}

PERTANYAAN:
{query}

JAWABAN:"""

        self._wait_for_rate_limit()
        response = self.model.generate_content(prompt)
        return response.text
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limit of 5 requests per minute"""
        current_time = time.time()
        time_since_last_request = current_time - GeminiClient._last_request_time
        
        if time_since_last_request < self._request_interval:
            wait_time = self._request_interval - time_since_last_request
            print(f"⏳ Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        GeminiClient._last_request_time = time.time()
    
    def summarize_chunks(self, chunks: list[str], max_length: int = 2000) -> str:
        """
        Summarize multiple chunks into a coherent context
        
        Args:
            chunks: List of text chunks
            max_length: Maximum length of summary
            
        Returns:
            Summarized context
        """
        combined = "\n\n---\n\n".join(chunks)
        
        # If combined text is short enough, return as is
        if len(combined) <= max_length:
            return combined
        
        prompt = f"""Ringkas informasi berikut menjadi teks yang koheren dan informatif.
Pertahankan detail penting dan angka-angka spesifik.
Maksimal {max_length} karakter.

TEKS:
{combined}

RINGKASAN:"""

        self._wait_for_rate_limit()
        response = self.model.generate_content(prompt)
        return response.text
