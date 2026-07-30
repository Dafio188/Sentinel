from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AIGate"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DATABASE_PATH: Path = BASE_DIR / "data" / "aigate.db"
    VAULT_PATH: Path = BASE_DIR / "data" / "vault.db"
    LOGS_DIR: Path = BASE_DIR / "logs"

settings = Settings()
