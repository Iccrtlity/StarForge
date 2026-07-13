"""LLM provider abstraction for different AI backends."""

from abc import ABC, abstractmethod
from typing import Optional
import os


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to guide behavior

        Returns:
            Generated text from the LLM
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available/configured."""
        pass


class OllamaProvider(LLMProvider):
    """Local Ollama provider - runs AI models locally."""

    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., 'mistral', 'llama2', 'neural-chat')
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        """Lazy load Ollama client."""
        if self._client is None:
            try:
                import ollama

                self._client = ollama
            except ImportError:
                raise ImportError(
                    "ollama package not installed. Install with: pip install ollama"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            self.client.list(base_url=self.base_url)
            return True
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Ollama."""
        if not self.is_available():
            raise RuntimeError(
                f"Ollama is not available at {self.base_url}. "
                "Make sure Ollama is running with: ollama serve"
            )

        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = self.client.generate(
                model=self.model,
                prompt=full_prompt,
                base_url=self.base_url,
                stream=False,
            )

            return response.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self, model: str = "gemini-pro", api_key: Optional[str] = None):
        """Initialize Gemini provider.

        Args:
            model: Model name (e.g., 'gemini-pro')
            api_key: API key (if None, will use GOOGLE_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._client = None

    @property
    def client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                if not self.api_key:
                    raise ValueError("GOOGLE_API_KEY environment variable not set")

                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Gemini."""
        if not self.is_available():
            raise RuntimeError(
                "Gemini API key not configured. "
                "Set GOOGLE_API_KEY environment variable."
            )

        try:
            genai = self.client
            model = genai.GenerativeModel(self.model)

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            response = model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}")


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API provider (OpenAI, Mistral, Azure, etc)."""

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
    ):
        """Initialize OpenAI-compatible provider.

        Args:
            model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')
            api_key: API key (if None, will use OPENAI_API_KEY env var)
            base_url: API base URL (for custom endpoints)
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI

                if not self.api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")

                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError(
                    "openai package not installed. Install with: pip install openai"
                )
        return self._client

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI-compatible API."""
        if not self.is_available():
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable."
            )

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=4000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")


def get_provider(
    provider_name: str, **kwargs
) -> LLMProvider:
    """Factory function to get an LLM provider.

    Args:
        provider_name: Provider name ('ollama', 'gemini', 'openai')
        **kwargs: Additional arguments for the provider

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is unknown
    """
    provider_map = {
        "ollama": OllamaProvider,
        "gemini": GeminiProvider,
        "openai": OpenAICompatibleProvider,
    }

    if provider_name not in provider_map:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Supported: {', '.join(provider_map.keys())}"
        )

    return provider_map[provider_name](**kwargs)
