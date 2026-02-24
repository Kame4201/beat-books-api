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

    # Circuit breaker
    CB_FAILURE_THRESHOLD: int = 5
    CB_RESET_TIMEOUT: float = 30.0

    model_config = {"env_file": ".env"}


settings = Settings()
