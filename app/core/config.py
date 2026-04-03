import json
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Finance Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: str = "*"
    DATABASE_URL: str
    FIRST_ADMIN_EMAIL: str = "admin@finance.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@1234"
    FIRST_ADMIN_NAME: str = "Super Admin"

    @property
    def allowed_origins_list(self) -> list[str]:
        v = self.ALLOWED_ORIGINS.strip()
        if not v:
            return ["*"]
        if v.startswith("["):
            return json.loads(v)
        return [item.strip() for item in v.split(",")]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()