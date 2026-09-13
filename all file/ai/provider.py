"""
LLM Provider Abstraction Layer
Supports Gemini, OpenAI, Groq, and an offline rule/tool-matching fallback provider.
"""

import abc
import json
import logging
import re
from typing import Dict, Any, List, Optional
from config.settings import settings

logger = logging.getLogger("JARVIS.AI.Provider")


class LLMProvider(abc.ABC):
    """Abstract base class for LLM backends."""

    @abc.abstractmethod
    async def generate_response(
        self, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None
    ) -> str:
        """Generate response from LLM."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini AI Provider."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning("Could not initialize google-genai client: %s", e)

    async def generate_response(
        self, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None
    ) -> str:
        if not self._client:
            raise RuntimeError("Gemini API key is not configured.")

        full_prompt = f"{system_prompt}\n\nUser: {prompt}"
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI API Provider (GPT-4o, GPT-4o-mini)."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name
        self._client = None
        if api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=api_key)
            except Exception:
                pass

    async def generate_response(
        self, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None
    ) -> str:
        if not self._client:
            raise RuntimeError("OpenAI API key is not configured.")

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for item in history:
                messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(model=self.model_name, messages=messages)
        return response.choices[0].message.content.strip()


class OfflineFallbackProvider(LLMProvider):
    """
    Offline local intent engine using pattern matching and keyword rule routing.
    Enables JARVIS to answer basic questions and trigger local tools without internet/API keys.
    """

    async def generate_response(
        self, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None
    ) -> str:
        p_lower = prompt.lower().strip()

        # System Metrics Intent
        if "cpu" in p_lower:
            return json.dumps({"tool": "get_cpu_usage", "kwargs": {}})
        if "ram" in p_lower or "memory" in p_lower:
            return json.dumps({"tool": "get_ram_usage", "kwargs": {}})
        if "disk" in p_lower or "storage" in p_lower:
            return json.dumps({"tool": "get_disk_usage", "kwargs": {}})
        if "battery" in p_lower:
            return json.dumps({"tool": "get_battery_status", "kwargs": {}})
        if "time" in p_lower or "date" in p_lower:
            return json.dumps({"tool": "get_current_time", "kwargs": {}})
        if "system" in p_lower or "specs" in p_lower:
            return json.dumps({"tool": "get_system_info", "kwargs": {}})

        # App Launch Intent
        if p_lower.startswith(("open ", "launch ", "start ")):
            app_target = (
                p_lower.replace("open ", "")
                .replace("launch ", "")
                .replace("start ", "")
                .replace("my ", "")
                .strip()
            )
            if app_target.startswith(("http", "www", "youtube", "google", "github")):
                return json.dumps({"tool": "open_website", "kwargs": {"url": app_target}})
            return json.dumps({"tool": "open_application", "kwargs": {"app_name": app_target}})

        # Close App Intent
        if p_lower.startswith(("close ", "stop ", "terminate ")):
            app_target = p_lower.replace("close ", "").replace("stop ", "").replace("terminate ", "").strip()
            return json.dumps({"tool": "close_application", "kwargs": {"app_name": app_target}})

        # Web Search Intent
        if "search" in p_lower or "find online" in p_lower:
            query = (
                p_lower.replace("search the web for ", "")
                .replace("search for ", "")
                .replace("search ", "")
                .strip()
            )
            return json.dumps({"tool": "web_search", "kwargs": {"query": query}})

        # Memory Intent
        if p_lower.startswith("remember that "):
            fact = p_lower.replace("remember that ", "").strip()
            parts = fact.split(" is ")
            if len(parts) == 2:
                return json.dumps({"tool": "remember_fact", "kwargs": {"key_term": parts[0].strip(), "value": parts[1].strip()}})
            return json.dumps({"tool": "remember_fact", "kwargs": {"key_term": "fact", "value": fact}})

        if "what do you remember" in p_lower or "remembered" in p_lower or "recall" in p_lower:
            return json.dumps({"tool": "get_memories", "kwargs": {"query": ""}})

        # Identity & Greeting
        if any(w in p_lower for w in ["who are you", "your name"]):
            return "I am JARVIS, your desktop AI assistant."
        if any(w in p_lower for w in ["hello", "hi", "hey jarvis"]):
            return "Online and ready. How may I assist you?"

        # Default helpful offline response
        return (
            "Offline Mode Active: No online AI API key detected. "
            "I can still run local commands like checking CPU/RAM, opening Chrome/Notepad, file operations, notes, and memory."
        )


def get_llm_provider() -> LLMProvider:
    """Factory function returning configured provider or fallback."""
    provider_type = settings.DEFAULT_AI_PROVIDER.lower()

    if provider_type == "gemini" and settings.GEMINI_API_KEY:
        try:
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.AI_MODEL)
        except Exception:
            pass

    if provider_type == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model_name=settings.AI_MODEL)
        except Exception:
            pass

    # Try any available key
    if settings.GEMINI_API_KEY:
        try:
            return GeminiProvider(api_key=settings.GEMINI_API_KEY)
        except Exception:
            pass

    if settings.OPENAI_API_KEY:
        try:
            return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        except Exception:
            pass

    logger.info("Using Offline Fallback Provider for local tool matching.")
    return OfflineFallbackProvider()
