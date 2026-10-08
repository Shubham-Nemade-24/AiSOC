"""Investigations API — list investigations and ledger entries."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Investigation, LedgerEntry, Alert

router = APIRouter(prefix="/api/investigations", tags=["Investigations"])


@router.get("")
async def list_investigations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Investigation).order_by(Investigation.created_at.desc()))
    investigations = result.scalars().all()
    out = []
    for inv in investigations:
        alert = await db.get(Alert, inv.alert_id)
        out.append({
            "id": inv.id, "alert_id": inv.alert_id,
            "alert_title": alert.title if alert else "Unknown",
            "alert_severity": alert.severity if alert else "unknown",
            "status": inv.status, "summary": inv.summary,
            "risk_score": inv.risk_score, "created_at": str(inv.created_at),
            "completed_at": str(inv.completed_at) if inv.completed_at else None,
        })
    return out


@router.get("/{inv_id}")
async def get_investigation(inv_id: str, db: AsyncSession = Depends(get_db)):
    inv = await db.get(Investigation, inv_id)
    if not inv:
        return {"error": "Not found"}
    alert = await db.get(Alert, inv.alert_id)
    entries = (await db.execute(
        select(LedgerEntry).where(LedgerEntry.investigation_id == inv.id).order_by(LedgerEntry.step_number)
    )).scalars().all()
    return {
        "id": inv.id, "alert_id": inv.alert_id,
        "alert_title": alert.title if alert else "Unknown",
        "alert_severity": alert.severity if alert else "unknown",
        "status": inv.status, "summary": inv.summary,
        "recommendation": inv.recommendation, "risk_score": inv.risk_score,
        "created_at": str(inv.created_at),
        "completed_at": str(inv.completed_at) if inv.completed_at else None,
        "ledger": [{"step": e.step_number, "agent": e.agent_name, "action": e.action,
                     "input": e.input_summary, "output": e.output_summary,
                     "decision": e.decision, "confidence": e.confidence,
                     "model": e.model_used, "tokens": e.tokens_used,
                     "duration_ms": e.duration_ms, "timestamp": str(e.timestamp)} for e in entries],
    }


@router.get("/ledger/all")
async def get_all_ledger(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LedgerEntry).order_by(LedgerEntry.timestamp.desc()).limit(100))
    entries = result.scalars().all()
    return [{"id": e.id, "investigation_id": e.investigation_id, "step": e.step_number,
             "agent": e.agent_name, "action": e.action, "output": e.output_summary[:200],
             "model": e.model_used, "tokens": e.tokens_used, "timestamp": str(e.timestamp)} for e in entries]
