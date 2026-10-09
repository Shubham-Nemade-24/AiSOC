"""Alerts API — CRUD + AI triage + investigation + OCSF fields."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Alert, Investigation, LedgerEntry
from app.services.ai_engine import triage_alert, investigate_alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("")
async def list_alerts(severity: str = None, status: str = None, db: AsyncSession = Depends(get_db)):
    q = select(Alert).order_by(Alert.created_at.desc())
    if severity:
        q = q.where(Alert.severity == severity)
    if status:
        q = q.where(Alert.status == status)
    result = await db.execute(q)
    return [_alert_dict(a) for a in result.scalars().all()]


@router.get("/{alert_id}")
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    return _alert_dict(alert)


@router.post("/{alert_id}/triage")
async def triage(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    return await triage_alert(alert, db)


@router.post("/{alert_id}/investigate")
async def investigate(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    inv = await investigate_alert(alert, db)
    entries = (await db.execute(
        select(LedgerEntry).where(LedgerEntry.investigation_id == inv.id).order_by(LedgerEntry.step_number)
    )).scalars().all()
    return {
        "id": inv.id, "alert_id": inv.alert_id, "status": inv.status,
        "summary": inv.summary, "recommendation": inv.recommendation,
        "risk_score": inv.risk_score, "created_at": str(inv.created_at),
        "completed_at": str(inv.completed_at) if inv.completed_at else None,
        "ledger": [{
            "step": e.step_number, "agent": e.agent_name, "action": e.action,
            "input": e.input_summary, "output": e.output_summary,
            "decision": e.decision, "confidence": e.confidence,
            "model": e.model_used, "tokens": e.tokens_used,
            "duration_ms": e.duration_ms, "timestamp": str(e.timestamp),
            "pseudonymized": e.pseudonymized,
            "content_hash": e.content_hash, "prev_hash": e.prev_hash,
        } for e in entries],
    }


@router.patch("/{alert_id}/status")
async def update_status(alert_id: str, status: str, db: AsyncSession = Depends(get_db)):
    alert = await db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = status
    await db.commit()
    return {"id": alert_id, "status": status}


def _alert_dict(a: Alert) -> dict:
    return {
        "id": a.id, "title": a.title, "description": a.description,
        "severity": a.severity, "status": a.status, "source": a.source,
        "mitre_tactic": a.mitre_tactic, "mitre_technique": a.mitre_technique,
        "mitre_id": a.mitre_id, "source_ip": a.source_ip, "dest_ip": a.dest_ip,
        "hostname": a.hostname, "username": a.username,
        "ai_verdict": a.ai_verdict, "ai_confidence": a.ai_confidence,
        "ai_reasoning": a.ai_reasoning, "ai_priority": a.ai_priority,
        # OCSF fields
        "ocsf_class_uid": a.ocsf_class_uid, "ocsf_category_uid": a.ocsf_category_uid,
        "ocsf_severity_id": a.ocsf_severity_id, "ocsf_type_uid": a.ocsf_type_uid,
        "correlation_group": a.correlation_group,
        "created_at": str(a.created_at), "updated_at": str(a.updated_at),
    }
