from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

    PROJECT_NAME: str = "NodeTrace"
    API_V1_PREFIX: str = "/api/v1"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    ENROLL_KEY: str
    ADMIN_SECRET_KEY: str

settings = Settings()