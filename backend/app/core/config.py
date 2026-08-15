import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Web Test Automation Platform"
    data_dir: str = os.getenv("DATA_DIR", str(ROOT_DIR / "data"))
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", str(ROOT_DIR / "data" / "artifacts"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(ROOT_DIR / 'data' / 'web_test_automation.db').as_posix()}",
    )
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "45"))
    playwright_headless: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() != "false"
    max_run_seconds: int = int(os.getenv("MAX_RUN_SECONDS", "45"))


settings = Settings()


def get_llm_config() -> dict:
    return {
        "base_url": settings.ollama_base_url,
        "model": settings.ollama_model,
        "timeout": settings.ollama_timeout,
    }
