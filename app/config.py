"""Application configuration loaded from environment variables.

Uses pydantic-settings to validate and type-check all configuration values at startup. If required value is missing, the app will
fail immediately with a clear error message - much better than a crashing randomly later.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the StockPilot application.
    
    All values are loaded from environment variables or the .env file.
    Type hints ensure values are automatically converted and validated.

    Example:

        >>> settings = Settings()
        >>> print (settings.APP_NAME)
        'StockPilot'
    """

    # application
    APP_NAME: str = "StockPilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "my-temporary-secret-key-change-later"  # Change this in production

    # db
    DATABASE_URL: str

    # redis
    REDIS_URL: str

    # jwt
    JWT_SECRET_KEY: str = "my-temporary-secret-key-change-later"  # Change this in production
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@stockpilot.com"
    EMAILS_FROM_NAME: str = "StockPilot"

    # S3
    AWS_ACCESS_KEY_ID: str = "" 
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: str = "stockpilot-uploads"

    # celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()