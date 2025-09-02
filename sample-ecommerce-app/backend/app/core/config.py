from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # CORS
    cors_allow_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database
    database_url: AnyUrl | str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce"

    # AWS Cognito
    aws_region: str = "us-east-1"
    cognito_user_pool_id: str = ""
    cognito_app_client_id: str = ""
    cognito_jwks_url: str | None = None

    # App
    environment: str = "local"


settings = Settings()

