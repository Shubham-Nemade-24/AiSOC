"""SQLAlchemy ORM models for AiSOC.

Includes OCSF schema fields for standards compliance and
SHA-256 integrity hashes on the Investigation Ledger for auditability.
"""
import uuid
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    """A security alert ingested into the SOC.
    
    Includes OCSF (Open Cybersecurity Schema Framework) fields for
    vendor-neutral event normalization per synopsis objective #1.
    """
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")
    source: Mapped[str] = mapped_column(String(100))

    # MITRE ATT&CK mapping
    mitre_tactic: Mapped[str] = mapped_column(String(100), nullable=True)
    mitre_technique: Mapped[str] = mapped_column(String(100), nullable=True)
    mitre_id: Mapped[str] = mapped_column(String(20), nullable=True)

    # Network observables
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    dest_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    hostname: Mapped[str] = mapped_column(String(256), nullable=True)
    username: Mapped[str] = mapped_column(String(256), nullable=True)
    raw_event: Mapped[str] = mapped_column(Text, nullable=True)

    # OCSF Schema Fields (Open Cybersecurity Schema Framework)
    ocsf_class_uid: Mapped[int] = mapped_column(Integer, nullable=True)       # OCSF event class (e.g., 2001=Security Finding)
    ocsf_category_uid: Mapped[int] = mapped_column(Integer, nullable=True)    # OCSF category (e.g., 2=Findings)
    ocsf_severity_id: Mapped[int] = mapped_column(Integer, nullable=True)     # OCSF severity (1=Info to 5=Critical)
    ocsf_activity_id: Mapped[int] = mapped_column(Integer, nullable=True)     # OCSF activity type
    ocsf_type_uid: Mapped[int] = mapped_column(Integer, nullable=True)        # Full OCSF type identifier

    # AI triage fields
    ai_verdict: Mapped[str] = mapped_column(String(30), nullable=True)
    ai_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    ai_priority: Mapped[int] = mapped_column(Integer, nullable=True)

    # Correlation
    correlation_group: Mapped[str] = mapped_column(String(36), nullable=True)  # UUID linking correlated alerts

    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
    investigations: Mapped[list["Investigation"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


# OCSF mapping helpers
SEVERITY_TO_OCSF = {"info": 1, "low": 2, "medium": 3, "high": 4, "critical": 5}
SOURCE_TO_OCSF_CLASS = {
    "EDR": 2001,         # Security Finding
    "SIEM": 2002,        # Detection Finding  
    "Firewall": 4001,    # Network Activity
    "IAM": 3001,         # Authentication
    "Cloud": 2003,       # Compliance Finding
    "Email": 4011,       # Email Activity
    "Network Monitor": 4001,  # Network Activity
}

def apply_ocsf(alert: Alert):
    """Apply OCSF schema fields to an alert based on its properties."""
    alert.ocsf_severity_id = SEVERITY_TO_OCSF.get(alert.severity, 3)
    alert.ocsf_class_uid = SOURCE_TO_OCSF_CLASS.get(alert.source, 2001)
    alert.ocsf_category_uid = 2  # Findings category
    alert.ocsf_activity_id = 1  # Create activity
    alert.ocsf_type_uid = (alert.ocsf_class_uid or 2001) * 100 + (alert.ocsf_activity_id or 1)


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
    """Immutable audit record with SHA-256 integrity hash chain.
    
    Each entry's hash incorporates the previous entry's hash, creating
    a tamper-evident chain per synopsis objective #5.
    """
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
    pseudonymized: Mapped[bool] = mapped_column(Boolean, default=False)

    # SHA-256 integrity hash chain
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True)   # SHA-256 of this entry's content
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=True)      # hash of previous entry (chain)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_now)
    investigation: Mapped["Investigation"] = relationship(back_populates="ledger_entries")

    def compute_hash(self, prev_hash: str = "0" * 64) -> str:
        """Compute SHA-256 hash of this entry's content + previous hash."""
        payload = json.dumps({
            "id": self.id,
            "investigation_id": self.investigation_id,
            "step": self.step_number,
            "agent": self.agent_name,
            "action": self.action,
            "input": self.input_summary[:500],
            "output": self.output_summary[:500],
            "decision": self.decision,
            "confidence": self.confidence,
            "model": self.model_used,
            "prev_hash": prev_hash,
        }, sort_keys=True)
        self.content_hash = hashlib.sha256(payload.encode()).hexdigest()
        self.prev_hash = prev_hash
        return self.content_hash
