"""Demo Endpoints — Trigger realistic alerts from any device (phone/tablet).

During a college demo, open these URLs from your PHONE browser
while the dashboard is visible on your laptop screen.
The alerts will appear in real-time on the SOC Dashboard.

Usage: http://<laptop-ip>:8000/demo  (shows all available triggers)
"""
import socket
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Alert, apply_ocsf
from app.services.ai_engine import triage_alert

router = APIRouter(prefix="/demo", tags=["Demo"])


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@router.get("", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Landing page with all demo trigger buttons — open this on your PHONE."""
    client_ip = request.client.host if request.client else "unknown"
    local_ip = _get_local_ip()
    hostname = socket.gethostname()

    return f"""<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AiSOC Demo Triggers</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,sans-serif; background:#0a0e1a; color:#e2e8f0; padding:20px; }}
  h1 {{ font-size:28px; font-weight:800; background:linear-gradient(135deg,#60a5fa,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }}
  .sub {{ color:#64748b; font-size:13px; margin-bottom:24px; }}
  .info {{ background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); border-radius:12px; padding:12px 16px; margin-bottom:20px; font-size:13px; }}
  .info span {{ color:#60a5fa; font-weight:600; }}
  .btn {{ display:block; width:100%; padding:16px; margin-bottom:12px; border:none; border-radius:14px; font-size:15px; font-weight:700; cursor:pointer; text-decoration:none; text-align:center; transition:all 0.3s; }}
  .btn:active {{ transform:scale(0.97); }}
  .critical {{ background:linear-gradient(135deg,#dc2626,#b91c1c); color:white; }}
  .high {{ background:linear-gradient(135deg,#ea580c,#c2410c); color:white; }}
  .medium {{ background:linear-gradient(135deg,#ca8a04,#a16207); color:white; }}
  .low {{ background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white; }}
  .info-btn {{ background:linear-gradient(135deg,#0891b2,#0e7490); color:white; }}
  .result {{ background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.2); border-radius:12px; padding:12px 16px; margin-top:16px; font-size:13px; display:none; }}
  .tag {{ display:inline-block; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600; margin-right:4px; }}
  .footer {{ text-align:center; color:#475569; font-size:11px; margin-top:24px; }}
</style></head><body>
<h1>🛡️ AiSOC Demo</h1>
<p class="sub">Trigger real-time security alerts from this device</p>

<div class="info">
  <span>Your Device:</span> {client_ip}<br>
  <span>SOC Target:</span> {hostname} ({local_ip})<br>
  <span>Dashboard:</span> http://{local_ip}:3000
</div>

<a class="btn critical" href="/demo/trigger/ransomware" onclick="fire(event,this)">🔴 Ransomware Attack</a>
<a class="btn critical" href="/demo/trigger/malware" onclick="fire(event,this)">🔴 Malware Detected</a>
<a class="btn high" href="/demo/trigger/brute-force" onclick="fire(event,this)">🟠 Brute Force Login</a>
<a class="btn high" href="/demo/trigger/port-scan" onclick="fire(event,this)">🟠 Port Scan</a>
<a class="btn medium" href="/demo/trigger/suspicious-login" onclick="fire(event,this)">🟡 Suspicious Login</a>
<a class="btn medium" href="/demo/trigger/data-exfil" onclick="fire(event,this)">🟡 Data Exfiltration</a>
<a class="btn low" href="/demo/trigger/recon" onclick="fire(event,this)">🔵 Recon Activity</a>
<a class="btn info-btn" href="/demo/trigger/device-detected" onclick="fire(event,this)">📱 New Device Detected</a>

<div id="result" class="result"></div>
<p class="footer">AiSOC — Gen AI Capstone Project<br>Group 4 · PCCOE Pune</p>

<script>
async function fire(e, btn) {{
  e.preventDefault();
  btn.style.opacity='0.6'; btn.textContent='⏳ Sending...';
  try {{
    const res = await fetch(btn.href);
    const data = await res.json();
    document.getElementById('result').style.display='block';
    document.getElementById('result').innerHTML = '✅ Alert created!<br><strong>'+data.title+'</strong><br>Severity: '+data.severity+' | Verdict: '+(data.ai_verdict||'triaging...');
    btn.textContent='✓ Sent!'; btn.style.opacity='1';
    setTimeout(()=>{{ btn.textContent=btn.href.split('/').pop().replace(/-/g,' ').toUpperCase(); }}, 2000);
  }} catch(err) {{
    document.getElementById('result').style.display='block';
    document.getElementById('result').innerHTML = '❌ Error: '+err.message;
    btn.style.opacity='1';
  }}
}}
</script>
</body></html>"""


async def _create_alert(data: dict, request: Request, db: AsyncSession) -> dict:
    """Helper: create alert, apply OCSF, auto-triage, return dict."""
    client_ip = request.client.host if request.client else "unknown"
    data["source_ip"] = client_ip
    data["hostname"] = socket.gethostname()
    data["is_synthetic"] = False
    data["created_at"] = datetime.now(timezone.utc)

    alert = Alert(**data)
    apply_ocsf(alert)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    await triage_alert(alert, db)

    return {"id": alert.id, "title": alert.title, "severity": alert.severity,
            "source_ip": client_ip, "ai_verdict": alert.ai_verdict,
            "ai_confidence": alert.ai_confidence, "status": "created & triaged"}


@router.get("/trigger/brute-force")
async def trigger_brute_force(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates brute force login from the requesting device."""
    return await _create_alert({
        "title": f"Brute Force Attack from Mobile Device",
        "description": f"Multiple failed authentication attempts detected from mobile device ({request.client.host}). "
                       f"52 failed SSH login attempts in 3 minutes targeting the SOC host. Pattern consistent with automated credential stuffing.",
        "severity": "high", "source": "EDR",
        "mitre_tactic": "Credential Access", "mitre_technique": "Brute Force", "mitre_id": "T1110",
        "dest_ip": _get_local_ip(), "username": "admin",
    }, request, db)


@router.get("/trigger/port-scan")
async def trigger_port_scan(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates network port scanning from the requesting device."""
    return await _create_alert({
        "title": f"Network Port Scan from Unregistered Device",
        "description": f"SYN scan detected from unregistered device ({request.client.host}). "
                       f"Scanning 1024 ports on the SOC host. Ports 22, 80, 443, 3000, 8000 found open. "
                       f"Device not in asset inventory — potential rogue device on network.",
        "severity": "high", "source": "Firewall",
        "mitre_tactic": "Discovery", "mitre_technique": "Network Service Discovery", "mitre_id": "T1046",
        "dest_ip": _get_local_ip(), "username": "unknown",
    }, request, db)


@router.get("/trigger/suspicious-login")
async def trigger_suspicious_login(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates impossible travel / suspicious login from mobile device."""
    return await _create_alert({
        "title": f"Suspicious Login from Unrecognized Device",
        "description": f"Login attempt detected from unrecognized mobile device ({request.client.host}). "
                       f"Device fingerprint does not match any registered endpoint. "
                       f"Geolocation suggests device is on the same network but is not in the corporate device inventory. "
                       f"Possible unauthorized access or BYOD policy violation.",
        "severity": "medium", "source": "IAM",
        "mitre_tactic": "Initial Access", "mitre_technique": "Valid Accounts", "mitre_id": "T1078",
        "dest_ip": _get_local_ip(), "username": "mobile_user",
    }, request, db)


@router.get("/trigger/ransomware")
async def trigger_ransomware(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates ransomware attack triggered from mobile C2."""
    return await _create_alert({
        "title": f"Ransomware C2 Communication from Mobile Device",
        "description": f"Command and control communication detected from mobile device ({request.client.host}). "
                       f"Device is sending encrypted payloads to the SOC host, triggering file encryption on shared drives. "
                       f"1,847 files renamed with .locked extension in the last 5 minutes. IMMEDIATE ACTION REQUIRED.",
        "severity": "critical", "source": "EDR",
        "mitre_tactic": "Impact", "mitre_technique": "Data Encrypted for Impact", "mitre_id": "T1486",
        "dest_ip": _get_local_ip(), "username": "system",
    }, request, db)


@router.get("/trigger/malware")
async def trigger_malware(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates malware delivery from mobile device."""
    return await _create_alert({
        "title": f"Malware Payload Delivered from Mobile Device",
        "description": f"Malicious executable transfer detected from mobile device ({request.client.host}). "
                       f"File 'update_installer.exe' (SHA256: a1b2c3d4e5...) matches known Cobalt Strike beacon signature. "
                       f"Payload delivered via SMB share. Endpoint protection quarantine failed.",
        "severity": "critical", "source": "EDR",
        "mitre_tactic": "Execution", "mitre_technique": "User Execution: Malicious File", "mitre_id": "T1204.002",
        "dest_ip": _get_local_ip(), "username": "svc_deploy",
    }, request, db)


@router.get("/trigger/data-exfil")
async def trigger_data_exfil(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates data exfiltration to mobile device."""
    return await _create_alert({
        "title": f"Data Exfiltration to Mobile Device",
        "description": f"Large data transfer detected to mobile device ({request.client.host}). "
                       f"2.3 GB of data from database server transferred via DNS tunneling to the mobile endpoint. "
                       f"Data includes customer PII from the production database. Transfer occurred outside business hours.",
        "severity": "medium", "source": "SIEM",
        "mitre_tactic": "Exfiltration", "mitre_technique": "Exfiltration Over Alternative Protocol", "mitre_id": "T1048",
        "dest_ip": _get_local_ip(), "username": "db_admin",
    }, request, db)


@router.get("/trigger/recon")
async def trigger_recon(request: Request, db: AsyncSession = Depends(get_db)):
    """Simulates reconnaissance from mobile device."""
    return await _create_alert({
        "title": f"Reconnaissance Activity from Mobile Device",
        "description": f"Network enumeration detected from mobile device ({request.client.host}). "
                       f"DNS lookups for internal hostnames, ARP scans of /24 subnet, and SNMP queries observed. "
                       f"Typical pre-attack reconnaissance pattern.",
        "severity": "low", "source": "Firewall",
        "mitre_tactic": "Reconnaissance", "mitre_technique": "Active Scanning", "mitre_id": "T1595",
        "dest_ip": _get_local_ip(), "username": "unknown",
    }, request, db)


@router.get("/trigger/device-detected")
async def trigger_device_detected(request: Request, db: AsyncSession = Depends(get_db)):
    """Detects the requesting device as new/unregistered."""
    return await _create_alert({
        "title": f"Unregistered Device Connected to Network",
        "description": f"New device detected on the network at IP {request.client.host}. "
                       f"Device is not registered in the corporate asset inventory. "
                       f"Device is communicating with the SOC server on port 8000. "
                       f"BYOD policy check required. Device fingerprint logged for review.",
        "severity": "medium", "source": "Network Monitor",
        "mitre_tactic": "Discovery", "mitre_technique": "System Network Connections Discovery", "mitre_id": "T1049",
        "dest_ip": _get_local_ip(), "username": "unknown",
    }, request, db)
