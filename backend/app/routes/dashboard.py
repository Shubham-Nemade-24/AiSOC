"""Dashboard API — aggregate metrics for the SOC console."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Alert, Investigation

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    by_severity = {}
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = (await db.execute(select(func.count(Alert.id)).where(Alert.severity == sev))).scalar() or 0
        by_severity[sev] = count
    by_status = {}
    for st in ["new", "triaged", "investigating", "resolved", "closed"]:
        count = (await db.execute(select(func.count(Alert.id)).where(Alert.status == st))).scalar() or 0
        by_status[st] = count
    by_source = {}
    rows = (await db.execute(select(Alert.source, func.count(Alert.id)).group_by(Alert.source))).all()
    for source, count in rows:
        by_source[source] = count
    inv_count = (await db.execute(select(func.count(Investigation.id)))).scalar() or 0
    inv_completed = (await db.execute(select(func.count(Investigation.id)).where(Investigation.status == "completed"))).scalar() or 0
    triaged = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict.isnot(None)))).scalar() or 0
    tp = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "true_positive"))).scalar() or 0
    return {
        "total_alerts": total, "by_severity": by_severity, "by_status": by_status,
        "by_source": by_source, "investigations": {"total": inv_count, "completed": inv_completed},
        "ai_triage": {"triaged": triaged, "true_positives": tp, "triage_rate": round(triaged / total * 100, 1) if total else 0},
    }
