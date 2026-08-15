from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
Path(settings.artifacts_dir).mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    columns = {column["name"] for column in inspect(engine).get_columns("test_cases")}
    with engine.begin() as connection:
        if "generation_source" not in columns:
            connection.execute(
                text("ALTER TABLE test_cases ADD COLUMN generation_source VARCHAR(30) NOT NULL DEFAULT 'fallback'")
            )
        if "intent_summary" not in columns:
            connection.execute(
                text("ALTER TABLE test_cases ADD COLUMN intent_summary TEXT NOT NULL DEFAULT ''")
            )
        if "session_id" not in columns:
            connection.execute(text("ALTER TABLE test_cases ADD COLUMN session_id INTEGER"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
