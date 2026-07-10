from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The default JWT signing key. It is public (checked into git) and therefore only
# safe for local dev / CI / tests. A real deployment MUST override SECRET_KEY;
# the startup guard below refuses to boot with this value outside dev/test.
DEFAULT_SECRET_KEY = "dev-insecure-secret-change-me-in-production"

# Environments where the public default key is tolerated (no real data at risk).
_DEV_ENVIRONMENTS = {"dev", "test"}


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
    # 5173 = vite dev server; 4173 = production `vite preview` (the frontend-prod
    # container used to exercise offline reads — ticket 06). Cross-origin API
    # responses must be CORS-allowed here or the service worker can't cache them.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # Deployment environment (ENVIRONMENT env var). "dev"/"test" tolerate the
    # public default secret; anything else (e.g. "production") must set a real
    # SECRET_KEY or the app refuses to boot — see the validator below.
    environment: str = "dev"

    # JWT signing. The default below is for local dev / CI only — production MUST
    # override SECRET_KEY with a strong random value (tokens signed with the
    # public default would otherwise be forgeable).
    secret_key: str = DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _forbid_default_secret_in_production(self) -> "Settings":
        # Fail fast at startup rather than silently signing forgeable tokens with
        # a key that is public in the repository. Only bites outside dev/test.
        if self.secret_key == DEFAULT_SECRET_KEY and self.environment not in _DEV_ENVIRONMENTS:
            raise ValueError(
                f"SECRET_KEY is unset (using the public default) in "
                f"environment={self.environment!r}. Set SECRET_KEY to a strong "
                f"random value before starting outside dev/test."
            )
        return self


settings = Settings()
