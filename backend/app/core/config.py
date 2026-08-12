from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "aigc-backend"
    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://aigc_user:change_me@localhost:5432/aigc_chat"
    )
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_doc: str = "document_vectors"
    qdrant_collection_memory: str = "memory_vectors"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    llm_proxy_base_url: str = ""
    llm_proxy_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
