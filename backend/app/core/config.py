from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration, sourced from environment variables.

    Values fall back to the defaults below when the corresponding env var is
    unset. In docker-compose and CI, DATABASE_URL is provided via the
    environment; locally for tests it is set to a SQLite URL (see the
    run-backend-tests-locally workflow).
    """

    # Overridden by DATABASE_URL in docker-compose / CI / local test runs.
    database_url: str = "postgresql://postgres:postgres@localhost/agriprofit"

    # Frontend origins permitted to call the API (CORS). Set CORS_ORIGINS as a
    # JSON array to override, e.g. '["https://app.example.com"]'.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # JWT signing. The default below is for local dev / CI only — production MUST
    # override SECRET_KEY with a strong random value (tokens signed with the
    # public default would otherwise be forgeable).
    secret_key: str = "dev-insecure-secret-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
