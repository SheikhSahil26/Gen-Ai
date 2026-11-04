"""Shared chat model configuration for Ollama Cloud's OpenAI-compatible API."""

from langchain_openai import ChatOpenAI

from ecommerce_ai.config.settings import settings


def create_chat_model(*, temperature: float = 0) -> ChatOpenAI:
    """Create a chat client configured for the deployed Ollama Cloud API."""
    return ChatOpenAI(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
        temperature=temperature,
    )
