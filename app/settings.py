from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # Groq/OpenAI configuration
    GROQ_API_KEY: str | None = None
    OPENAI_BASE_URL: str = "https://api.groq.com/openai/v1"

    # SerpAPI configuration
    SERPAPI_API_KEY: str | None = None

    # App configuration
    APP_NAME: str = "website-backend-python"
    ENV: str = "development"  # values: development|production


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# Eagerly resolve a singleton for simple imports
settings = get_settings()


