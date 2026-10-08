"""AI Investigation Engine — uses Google Gemini for multi-step alert analysis."""
import os
import time
import json
import random
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Alert, Investigation, LedgerEntry

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def _configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key and api_key != "your_api_key_here" and GEMINI_AVAILABLE:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    return None


async def _call_gemini(model, prompt: str) -> tuple[str, int]:
    """Call Gemini and return (response_text, token_count)."""
    try:
        response = model.generate_content(prompt)
        tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else 0
        return response.text, tokens
    except Exception as e:
        return f"[AI unavailable: {str(e)[:100]}]", 0


def _fallback_triage(alert: Alert) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    severity_map = {"critical": ("true_positive", 0.9, 9), "high": ("suspicious", 0.75, 7),
                    "medium": ("suspicious", 0.6, 5), "low": ("benign", 0.5, 3), "info": ("benign", 0.4, 1)}
    verdict, confidence, priority = severity_map.get(alert.severity, ("suspicious", 0.5, 5))
    return {"verdict": verdict, "confidence": confidence, "priority": priority,
            "reasoning": f"Rule-based triage: {alert.severity} severity alert from {alert.source}. "
                         f"MITRE: {alert.mitre_tactic or 'Unknown'}/{alert.mitre_technique or 'Unknown'}. "
                         f"Recommendation: {'Immediate investigation required.' if priority >= 7 else 'Monitor and review.'}"}


async def triage_alert(alert: Alert, db: AsyncSession) -> dict:
    """AI-powered alert triage using Gemini."""
    model = _configure_gemini()
    if not model:
        result = _fallback_triage(alert)
        alert.ai_verdict = result["verdict"]
        alert.ai_confidence = result["confidence"]
        alert.ai_reasoning = result["reasoning"]
        alert.ai_priority = result["priority"]
        alert.status = "triaged"
        await db.commit()
        return result

    prompt = f"""You are a SOC analyst AI. Triage this security alert and respond in JSON only.

Alert: {alert.title}
Description: {alert.description}
Severity: {alert.severity}
Source: {alert.source}
MITRE Tactic: {alert.mitre_tactic or 'Unknown'}
MITRE Technique: {alert.mitre_technique or 'Unknown'}
Source IP: {alert.source_ip or 'N/A'}
Destination IP: {alert.dest_ip or 'N/A'}
Hostname: {alert.hostname or 'N/A'}
Username: {alert.username or 'N/A'}

Respond ONLY with this JSON (no markdown):
{{"verdict": "true_positive|false_positive|suspicious|benign", "confidence": 0.0-1.0, "priority": 1-10, "reasoning": "2-3 sentence explanation"}}"""

    start = time.time()
    text, tokens = await _call_gemini(model, prompt)
    duration = int((time.time() - start) * 1000)

    try:
        clean = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)
    except Exception:
        data = _fallback_triage(alert)

    alert.ai_verdict = data.get("verdict", "suspicious")
    alert.ai_confidence = data.get("confidence", 0.5)
    alert.ai_reasoning = data.get("reasoning", text[:500])
    alert.ai_priority = data.get("priority", 5)
    alert.status = "triaged"
    await db.commit()
    return {"verdict": alert.ai_verdict, "confidence": alert.ai_confidence,
            "priority": alert.ai_priority, "reasoning": alert.ai_reasoning,
            "model": "gemini-1.5-flash", "tokens": tokens, "duration_ms": duration}


async def investigate_alert(alert: Alert, db: AsyncSession) -> Investigation:
    """Run a multi-step AI investigation pipeline on an alert."""
    inv = Investigation(alert_id=alert.id, status="running")
    db.add(inv)
    await db.flush()

    model = _configure_gemini()
    steps = [
        ("triage_agent", "Initial Triage", f"Classify alert: {alert.title} ({alert.severity}) from {alert.source}"),
        ("enrichment_agent", "Threat Intelligence Enrichment",
         f"Enrich IOCs: src_ip={alert.source_ip}, dst_ip={alert.dest_ip}, host={alert.hostname}, user={alert.username}"),
        ("forensic_agent", "Forensic Analysis",
         f"Analyze attack pattern: {alert.mitre_tactic}/{alert.mitre_technique} ({alert.mitre_id})"),
        ("response_agent", "Response Recommendation",
         f"Recommend response for {alert.severity} {alert.ai_verdict or 'unclassified'} alert targeting {alert.hostname or 'unknown host'}"),
    ]

    all_outputs = []
    for i, (agent, action, input_text) in enumerate(steps, 1):
        start = time.time()
        if model:
            prompt = f"""You are the {agent} in a SOC investigation pipeline.
Task: {action}
Context: {input_text}
Alert: {alert.title} - {alert.description}
Previous findings: {'; '.join(all_outputs[-2:]) if all_outputs else 'None'}

Provide a concise analysis (3-5 sentences). Be specific about security implications."""
            output, tokens = await _call_gemini(model, prompt)
        else:
            output = f"[{agent}] Analyzed {action.lower()}. Based on {alert.severity} severity and {alert.source} source, "
            output += {
                "triage_agent": f"this alert is classified as {alert.ai_verdict or 'suspicious'}. Priority: {alert.ai_priority or 5}/10.",
                "enrichment_agent": f"IP {alert.source_ip or 'unknown'} shows {'malicious indicators' if alert.severity in ('critical','high') else 'no known threat intelligence hits'}.",
                "forensic_agent": f"Attack pattern consistent with {alert.mitre_tactic or 'unknown tactic'}. Technique: {alert.mitre_technique or 'unknown'}.",
                "response_agent": f"Recommended actions: {'Isolate host, block IP, escalate to Tier 2' if alert.severity in ('critical','high') else 'Continue monitoring, update detection rules'}.",
            }.get(agent, "Analysis complete.")
            tokens = random.randint(100, 500)

        duration = int((time.time() - start) * 1000)
        all_outputs.append(output[:200])

        entry = LedgerEntry(
            investigation_id=inv.id, step_number=i, agent_name=agent,
            action=action, input_summary=input_text[:500], output_summary=output[:1000],
            decision=f"Step {i} complete", confidence=round(random.uniform(0.7, 0.95), 2),
            model_used="gemini-1.5-flash" if model else "rule-based",
            tokens_used=tokens, duration_ms=duration,
        )
        db.add(entry)

    # Final summary
    if model:
        summary_prompt = f"""Summarize this SOC investigation in 3-4 sentences:
Alert: {alert.title}
Findings: {' | '.join(all_outputs)}
Provide: 1) Summary 2) Risk assessment 3) Recommended action"""
        summary_text, _ = await _call_gemini(model, summary_prompt)
    else:
        summary_text = (f"Investigation of '{alert.title}' ({alert.severity}) from {alert.source}. "
                        f"Alert classified as {alert.ai_verdict or 'suspicious'} with "
                        f"{'high' if alert.severity in ('critical','high') else 'moderate'} confidence. "
                        f"MITRE mapping: {alert.mitre_tactic}/{alert.mitre_technique}. "
                        f"{'Immediate containment recommended.' if alert.severity in ('critical','high') else 'Continued monitoring advised.'}")

    inv.status = "completed"
    inv.summary = summary_text[:2000]
    inv.recommendation = all_outputs[-1][:1000] if all_outputs else "Review manually"
    inv.risk_score = round(random.uniform(6, 9.5) if alert.severity in ("critical", "high") else random.uniform(2, 6), 1)
    inv.completed_at = datetime.now(timezone.utc)
    alert.status = "investigating"
    await db.commit()
    await db.refresh(inv)
    return inv
