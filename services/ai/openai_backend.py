"""OpenAI API backend for the Jarvis AI service."""

from typing import AsyncGenerator

from loguru import logger

from services.ai.base import AIBase


class OpenAIBackend(AIBase):
    """Connects to the OpenAI API (or any OpenAI-compatible endpoint).

    Requires the OPENAI_API_KEY environment variable (loaded from .env).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = None

        if api_key:
            self._init_client()
        else:
            logger.warning("OpenAIBackend: no API key provided. Set OPENAI_API_KEY in .env")

    def _init_client(self) -> None:
        try:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=self._api_key)
            logger.info(f"OpenAI backend ready (model={self._model})")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")

    async def chat(self, messages: list[dict[str, str]]) -> str:
        """Send messages and return a complete response string."""
        if not self._client:
            return "OpenAI is not configured. Please add OPENAI_API_KEY to your .env file."

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            text = response.choices[0].message.content or ""
            logger.debug(f"OpenAI response ({len(text)} chars)")
            return text
        except Exception as exc:
            logger.exception("OpenAI chat request failed")
            return f"I'm having trouble connecting to OpenAI: {exc}"

    async def stream_chat(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from OpenAI."""
        if not self._client:
            yield "OpenAI is not configured. Please add OPENAI_API_KEY to your .env file."
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
            logger.exception("OpenAI streaming request failed")
            yield f"I'm having trouble connecting to OpenAI: {exc}"

    def is_available(self) -> bool:
        return self._client is not None
