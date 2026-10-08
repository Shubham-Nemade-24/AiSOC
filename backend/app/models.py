"""SQLAlchemy ORM models for AiSOC."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")
    source: Mapped[str] = mapped_column(String(100))
    mitre_tactic: Mapped[str] = mapped_column(String(100), nullable=True)
    mitre_technique: Mapped[str] = mapped_column(String(100), nullable=True)
    mitre_id: Mapped[str] = mapped_column(String(20), nullable=True)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    dest_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    hostname: Mapped[str] = mapped_column(String(256), nullable=True)
    username: Mapped[str] = mapped_column(String(256), nullable=True)
    raw_event: Mapped[str] = mapped_column(Text, nullable=True)
    ai_verdict: Mapped[str] = mapped_column(String(30), nullable=True)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    ai_priority: Mapped[int] = mapped_column(Integer, nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
    investigations: Mapped[list["Investigation"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class Investigation(Base):
    __tablename__ = "investigations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey("alerts.id"))
    status: Mapped[str] = mapped_column(String(20), default="running")
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    alert: Mapped["Alert"] = relationship(back_populates="investigations")
    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    investigation_id: Mapped[str] = mapped_column(String(36), ForeignKey("investigations.id"))
    step_number: Mapped[int] = mapped_column(Integer)
    agent_name: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    input_summary: Mapped[str] = mapped_column(Text)
    output_summary: Mapped[str] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    model_used: Mapped[str] = mapped_column(String(50), default="gemini-1.5-flash")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_now)
    investigation: Mapped["Investigation"] = relationship(back_populates="ledger_entries")
