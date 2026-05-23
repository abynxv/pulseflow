from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    database_url: str = "postgresql+asyncpg://parseflow:parseflow@localhost:5432/parseflow"

    max_file_size_mb: int = 10
    max_text_length: int = 50_000
    max_retries: int = 3


settings = Settings()
