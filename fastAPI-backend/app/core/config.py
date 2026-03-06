from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "User Registration API"
    VERSION: str = "1.0.0"
    
    # Database
    # Provide a sensible default so importing settings doesn't fail in test/dev without an .env
    MONGO_URL: str = Field("mongodb://localhost:27017", alias="MONGO_URL")
    DB_NAME: str = "ITVE_Database"

    # Security - map the .env name to your Python variable name
    # Provide defaults to avoid hard failures during import; production should set real secrets
    SECRET_KEY: str = Field("change-me-secret", alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Business Logic
    ADMIN_SECRET_CODE: str = Field("", alias="ADMIN_SECRET_CODE")
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}

    # This tells Pydantic to automatically load from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()