from pathlib import Path

from pydantic_settings import BaseSettings

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    data_dir: Path = ROOT / "data"
    model_path: Path = ROOT / "artifacts" / "model.joblib"
    database_url: str | None = None
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
