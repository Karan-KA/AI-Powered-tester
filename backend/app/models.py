import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(180), nullable=False)
    target_url = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    test_cases = relationship("TestCase", back_populates="session", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        return self.title


# Alias for Report compatibility
WorkspaceSession = TestSession


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=True, index=True)
    name = Column(String(180), nullable=False)
    target_url = Column(String(1000), nullable=False)
    requirement = Column(Text, nullable=False)
    steps_json = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    generation_source = Column(String(30), nullable=False, default="fallback")
    intent_summary = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("TestSession", back_populates="test_cases")
    runs = relationship("TestRun", back_populates="test_case", cascade="all, delete-orphan")

    @property
    def prompt(self) -> str:
        return self.requirement


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    status = Column(String(20), nullable=False, default="warning")
    duration_ms = Column(Float, nullable=False, default=0)
    summary = Column(Text, nullable=False, default="")
    error_summary = Column(Text, nullable=False, default="")
    logs_json = Column(Text, nullable=False, default="[]")
    screenshots_json = Column(Text, nullable=False, default="[]")
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    test_case = relationship("TestCase", back_populates="runs")

    @property
    def screenshot(self) -> str | None:
        try:
            shots = json.loads(self.screenshots_json or "[]")
            return shots[0] if shots else None
        except Exception:
            return None

    @property
    def logs(self) -> str:
        return self.logs_json

    @property
    def error_msg(self) -> str:
        return self.error_summary

    @property
    def executed_at(self) -> datetime:
        return self.started_at
