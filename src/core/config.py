from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for beat-books-api gateway."""

    # Service URLs (for HTTP-based communication)
    DATA_SERVICE_URL: str = "http://localhost:8001"
    MODEL_SERVICE_URL: str = "http://localhost:8002"

    # App
    API_HOST: str = "0.0.0.0"  # nosec B104 - intentional for containerized deployment
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_PREDICTIONS: str = "20/minute"

    # Authentication
    API_KEYS: str = ""  # Comma-separated list of valid API keys

    model_config = {"env_file": ".env"}


settings = Settings()
