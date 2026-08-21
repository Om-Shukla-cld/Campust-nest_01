"""
Central configuration. Every value can be overridden from a `.env` file placed
next to this file (see `.env.example`) or from real environment variables.
"""
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CampusNest API")
    VERSION: str = "1.0.0"
    DEBUG: bool = _bool("DEBUG", True)

    # Database
    USE_SQLITE: bool = _bool("USE_SQLITE", True)
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "campusnest.db")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/campusnest"
    )

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "campusnest-dev-secret-key-change-me-in-production-0123456789")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DEMO_OTP: str = os.getenv("DEMO_OTP", "1234")
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))

    # Demo moderator phone (see README "Demo Credentials")
    MODERATOR_PHONE: str = os.getenv("MODERATOR_PHONE", "+910000000000")

    # App behaviour
    SEED_DEMO_DATA: bool = _bool("SEED_DEMO_DATA", True)
    ALLOWED_ORIGINS: List[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
        if o.strip()
    ]

    # Optional payments
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "")

    @property
    def sqlalchemy_url(self) -> str:
        if self.USE_SQLITE:
            path = Path(self.SQLITE_PATH)
            if not path.is_absolute():
                path = BASE_DIR / path
            return f"sqlite:///{path}"
        return self.DATABASE_URL

    @property
    def payments_enabled(self) -> bool:
        return bool(self.RAZORPAY_KEY_ID and self.RAZORPAY_KEY_SECRET)


settings = Settings()
