from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+psycopg://localhost/flight_analyzer"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300

    # Amadeus API
    amadeus_client_id: str = ""
    amadeus_client_secret: str = ""
    amadeus_hostname: str = "test"  # "test" | "production"

    # Claude API
    anthropic_api_key: str = ""
    agent_model: str = "claude-opus-4-7"
    agent_fast_model: str = "claude-haiku-4-5-20251001"

    # App
    debug: bool = False
    log_level: str = "INFO"


settings = Settings()
