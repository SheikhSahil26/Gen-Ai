import os

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = Field(default="", validation_alias="QDRANT_API_KEY")
    qdrant_collection: str = "ecommerce_support"
    auth_cookie_secure: bool = True
    frontend_url: str = Field(default="", validation_alias="FRONTEND_URL")
    ollama_api_key: str = Field(default="", validation_alias="OLLAMA_API_KEY")
    ollama_base_url: str = "https://ollama.com/v1"
    ollama_model: str = "gpt-oss:120b-cloud"
    langsmith_tracing: bool = Field(
        default=True,
        validation_alias=AliasChoices("LANGSMITH_TRACING", "LANGCHAIN_TRACING_V2"),
    )
    langsmith_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"),
    )
    langsmith_project: str = Field(
        default="multi-ai-agent",
        validation_alias=AliasChoices("LANGSMITH_PROJECT", "LANGCHAIN_PROJECT"),
    )
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        validation_alias=AliasChoices("LANGSMITH_ENDPOINT", "LANGCHAIN_ENDPOINT"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        if self.frontend_url:
            for item in self.frontend_url.split(","):
                clean_item = item.strip().rstrip("/")
                if clean_item and clean_item not in origins:
                    origins.append(clean_item)
        return origins

    def configure_langsmith(self) -> None:
        # Respect explicit process environment values; otherwise apply values
        # loaded from .env by pydantic-settings for LangChain's tracer.
        os.environ.setdefault("LANGSMITH_TRACING", str(self.langsmith_tracing).lower())
        if self.langsmith_api_key:
            os.environ.setdefault("LANGSMITH_API_KEY", self.langsmith_api_key)
        os.environ.setdefault("LANGSMITH_PROJECT", self.langsmith_project)
        os.environ.setdefault("LANGSMITH_ENDPOINT", self.langsmith_endpoint)


settings = Settings()
