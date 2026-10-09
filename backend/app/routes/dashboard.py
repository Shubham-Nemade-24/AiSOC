"""Dashboard API — aggregate metrics, evaluation harness, and correlation."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Alert, Investigation, LedgerEntry
from app.services.correlation import correlate_alerts

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
    fp = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "false_positive"))).scalar() or 0
    suspicious = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "suspicious"))).scalar() or 0
    benign = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "benign"))).scalar() or 0
    return {
        "total_alerts": total, "by_severity": by_severity, "by_status": by_status,
        "by_source": by_source, "investigations": {"total": inv_count, "completed": inv_completed},
        "ai_triage": {
            "triaged": triaged, "true_positives": tp, "false_positives": fp,
            "suspicious": suspicious, "benign": benign,
            "triage_rate": round(triaged / total * 100, 1) if total else 0,
        },
    }


@router.get("/evaluation")
async def get_evaluation_metrics(db: AsyncSession = Depends(get_db)):
    """Evaluation harness — measures triage accuracy and pipeline performance."""
    total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    triaged = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict.isnot(None)))).scalar() or 0
    tp = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "true_positive"))).scalar() or 0
    fp = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "false_positive"))).scalar() or 0
    suspicious = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "suspicious"))).scalar() or 0
    benign = (await db.execute(select(func.count(Alert.id)).where(Alert.ai_verdict == "benign"))).scalar() or 0

    # Alert reduction rate: how many alerts were reduced by triage (FP + benign / total)
    noise_reduced = fp + benign
    reduction_rate = round(noise_reduced / triaged * 100, 1) if triaged else 0

    # Average confidence
    avg_conf = (await db.execute(select(func.avg(Alert.ai_confidence)).where(Alert.ai_confidence.isnot(None)))).scalar()
    avg_confidence = round(float(avg_conf), 3) if avg_conf else 0

    # Investigation metrics
    inv_total = (await db.execute(select(func.count(Investigation.id)))).scalar() or 0
    inv_completed = (await db.execute(select(func.count(Investigation.id)).where(Investigation.status == "completed"))).scalar() or 0
    avg_risk = (await db.execute(select(func.avg(Investigation.risk_score)).where(Investigation.risk_score.isnot(None)))).scalar()

    # Ledger integrity
    ledger_count = (await db.execute(select(func.count(LedgerEntry.id)))).scalar() or 0
    hashed_count = (await db.execute(select(func.count(LedgerEntry.id)).where(LedgerEntry.content_hash.isnot(None)))).scalar() or 0
    pseudonymized_count = (await db.execute(select(func.count(LedgerEntry.id)).where(LedgerEntry.pseudonymized == True))).scalar() or 0

    # Severity distribution of true positives
    tp_by_sev = {}
    for sev in ["critical", "high", "medium", "low"]:
        count = (await db.execute(
            select(func.count(Alert.id)).where(Alert.ai_verdict == "true_positive", Alert.severity == sev)
        )).scalar() or 0
        tp_by_sev[sev] = count

    return {
        "triage_metrics": {
            "total_alerts": total,
            "triaged": triaged,
            "triage_rate_pct": round(triaged / total * 100, 1) if total else 0,
            "verdicts": {"true_positive": tp, "false_positive": fp, "suspicious": suspicious, "benign": benign},
            "alert_reduction_rate_pct": reduction_rate,
            "avg_confidence": avg_confidence,
            "true_positives_by_severity": tp_by_sev,
        },
        "investigation_metrics": {
            "total_investigations": inv_total,
            "completed": inv_completed,
            "completion_rate_pct": round(inv_completed / inv_total * 100, 1) if inv_total else 0,
            "avg_risk_score": round(float(avg_risk), 1) if avg_risk else 0,
        },
        "ledger_integrity": {
            "total_entries": ledger_count,
            "hashed_entries": hashed_count,
            "hash_coverage_pct": round(hashed_count / ledger_count * 100, 1) if ledger_count else 0,
            "pseudonymized_entries": pseudonymized_count,
        },
    }


@router.get("/correlations")
async def get_correlations(db: AsyncSession = Depends(get_db)):
    """Get correlated alert groups."""
    clusters = await correlate_alerts(db)
    return {"correlations": clusters, "total_groups": len(clusters)}
