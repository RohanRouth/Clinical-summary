from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # FHIR Configuration
    fhir_base_url: str = "http://hapi.fhir.org/baseR4"
    fhir_timeout: int = 30

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
