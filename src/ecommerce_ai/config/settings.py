import os

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
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

    def configure_langsmith(self) -> None:
        # Respect explicit process environment values; otherwise apply values
        # loaded from .env by pydantic-settings for LangChain's tracer.
        os.environ.setdefault("LANGSMITH_TRACING", str(self.langsmith_tracing).lower())
        if self.langsmith_api_key:
            os.environ.setdefault("LANGSMITH_API_KEY", self.langsmith_api_key)
        os.environ.setdefault("LANGSMITH_PROJECT", self.langsmith_project)
        os.environ.setdefault("LANGSMITH_ENDPOINT", self.langsmith_endpoint)


settings = Settings()
