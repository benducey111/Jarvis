"""Ollama local AI backend — uses the OpenAI-compatible REST API."""

from typing import AsyncGenerator

from loguru import logger

from services.ai.base import AIBase


class OllamaBackend(AIBase):
    """Connects to a local Ollama server at http://localhost:11434/v1.

    Requires Ollama to be installed and running:  https://ollama.ai
    Models can be pulled with:  ollama pull llama3
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "llama3",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        self._base_url = base_url
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

        self._init_client()

    def _init_client(self) -> None:
        try:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key="ollama",   # Ollama ignores the key value
                base_url=self._base_url,
            )
            logger.info(f"Ollama backend configured (model={self._model}, url={self._base_url})")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")

    async def chat(self, messages: list[dict[str, str]]) -> str:
        if not self._client:
            return "Ollama backend is not available."

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            text = response.choices[0].message.content or ""
            logger.debug(f"Ollama response ({len(text)} chars)")
            return text
        except Exception as exc:
            logger.exception("Ollama chat request failed")
            return (
                f"I couldn't reach Ollama ({exc}). "
                "Make sure Ollama is running: ollama serve"
            )

    async def stream_chat(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        if not self._client:
            yield "Ollama backend is not available."
            return

        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            logger.exception("Ollama streaming request failed")
            yield f"Ollama error: {exc}"

    def is_available(self) -> bool:
        return self._client is not None
