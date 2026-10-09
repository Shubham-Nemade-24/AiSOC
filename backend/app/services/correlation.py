"""Alert Correlation & Fusion Engine — groups related alerts by shared entities and time.

Performs temporal and entity-based correlation:
1. Groups alerts sharing IPs, hostnames, or usernames within a time window
2. Creates fused alert groups with escalated severity
3. Links related alerts for investigation context
"""
import asyncio
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import Alert

_running = False

# Correlation config
CORRELATION_WINDOW_MINUTES = 60   # group alerts within this time window
MIN_CLUSTER_SIZE = 2              # minimum alerts to form a correlated group


def _extract_entities(alert: Alert) -> set[str]:
    """Extract all entity identifiers from an alert for correlation matching."""
    entities = set()
    if alert.source_ip and alert.source_ip not in ("N/A", "multiple", "unknown"):
        entities.add(f"ip:{alert.source_ip}")
    if alert.dest_ip and alert.dest_ip not in ("N/A", "multiple", "unknown"):
        entities.add(f"ip:{alert.dest_ip}")
    if alert.hostname and alert.hostname not in ("N/A", "unknown"):
        entities.add(f"host:{alert.hostname}")
    if alert.username and alert.username not in ("N/A", "multiple", "unknown", "system"):
        entities.add(f"user:{alert.username}")
    return entities


async def correlate_alerts(db: AsyncSession) -> list[dict]:
    """Find groups of correlated alerts based on shared entities within time windows."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=CORRELATION_WINDOW_MINUTES)
    result = await db.execute(
        select(Alert).where(Alert.created_at >= cutoff).order_by(Alert.created_at.desc())
    )
    alerts = result.scalars().all()

    if len(alerts) < MIN_CLUSTER_SIZE:
        return []

    # Build entity -> alert mapping
    entity_map: dict[str, list[Alert]] = defaultdict(list)
    for alert in alerts:
        for entity in _extract_entities(alert):
            entity_map[entity].append(alert)

    # Find clusters: groups of alerts sharing entities
    visited = set()
    clusters = []

    for entity, alert_group in entity_map.items():
        if len(alert_group) < MIN_CLUSTER_SIZE:
            continue

        alert_ids = frozenset(a.id for a in alert_group)
        if alert_ids in visited:
            continue
        visited.add(alert_ids)

        # Expand cluster: find all alerts connected through shared entities
        cluster_alerts = set(alert_group)
        expanded = True
        while expanded:
            expanded = False
            new_entities = set()
            for a in cluster_alerts:
                new_entities |= _extract_entities(a)
            for e in new_entities:
                for a in entity_map.get(e, []):
                    if a not in cluster_alerts:
                        cluster_alerts.add(a)
                        expanded = True

        if len(cluster_alerts) >= MIN_CLUSTER_SIZE:
            # Calculate cluster severity (highest in group)
            sev_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
            max_sev = max(cluster_alerts, key=lambda a: sev_order.get(a.severity, 0))

            # Shared entities
            shared = set()
            for a in cluster_alerts:
                shared |= _extract_entities(a)

            clusters.append({
                "shared_entities": list(shared),
                "alert_count": len(cluster_alerts),
                "alert_ids": [a.id for a in cluster_alerts],
                "alert_titles": [a.title for a in cluster_alerts],
                "max_severity": max_sev.severity,
                "time_span_minutes": _time_span(cluster_alerts),
                "mitre_tactics": list(set(a.mitre_tactic for a in cluster_alerts if a.mitre_tactic)),
            })

    # Sort by alert count descending
    clusters.sort(key=lambda c: c["alert_count"], reverse=True)
    return clusters


def _time_span(alerts: set[Alert]) -> int:
    """Calculate time span of alerts in minutes."""
    times = [a.created_at for a in alerts if a.created_at]
    if len(times) < 2:
        return 0
    # Handle timezone-naive datetimes
    return int((max(times) - min(times)).total_seconds() / 60)


async def start_correlation_engine(interval: int = 60):
    """Background task: runs correlation every `interval` seconds."""
    global _running
    if _running:
        return
    _running = True
    print(f"[Correlation] Engine started — running every {interval}s")
    while _running:
        try:
            async with async_session() as db:
                clusters = await correlate_alerts(db)
                if clusters:
                    print(f"[Correlation] Found {len(clusters)} correlated alert groups")
        except Exception as e:
            print(f"[Correlation] Error: {e}")
        await asyncio.sleep(interval)


def stop_correlation_engine():
    global _running
    _running = False
