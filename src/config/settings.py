from pathlib import Path
from typing import Optional, List

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEV_MODE: bool = False
    DEBUG: bool = True

    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432

    SQLITE_PATH: str = "sqlite.db"
    START_URL: str = "https://auto.ria.com/uk/car/used/"
    SCRAPE_REPEAT_AFTER_MINUTES: Optional[int] = None
    DUMP_TIME: str

    PROXIES: Optional[List[str]] = Field(default=None)

    @field_validator("PROXIES", mode="before")
    @classmethod
    def parse_proxies(cls, v):
        if isinstance(v, str):
            return [proxy.strip() for proxy in v.split(",") if proxy.strip()]
        return v

    @property
    def db_url(self) -> str:
        if self.DEV_MODE:
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

        return (f"postgresql+asyncpg://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file=Path(__file__).resolve().parent.parent.parent / ".env"


settings = Settings()