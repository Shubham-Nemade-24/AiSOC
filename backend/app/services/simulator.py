"""Real-time alert simulator — generates and auto-triages alerts."""
import asyncio
import random
import uuid
from datetime import datetime, timezone
from app.database import async_session
from app.models import Alert, apply_ocsf
from app.services.ai_engine import triage_alert

TEMPLATES = [
    {"title": "Brute Force Login — {host}", "description": "{count} failed login attempts from {src_ip} in {mins} minutes targeting {host}.", "severity": "high", "source": "EDR", "mitre_tactic": "Credential Access", "mitre_technique": "Brute Force", "mitre_id": "T1110"},
    {"title": "Suspicious Outbound DNS — {host}", "description": "High volume DNS queries to {domain} from {host}. Potential C2 or data exfiltration via DNS tunneling.", "severity": "critical", "source": "Firewall", "mitre_tactic": "Command and Control", "mitre_technique": "Application Layer Protocol: DNS", "mitre_id": "T1071.004"},
    {"title": "Malware Hash Match — {host}", "description": "File with known malware hash {hash} detected on {host} by endpoint agent. File: {filename}", "severity": "critical", "source": "EDR", "mitre_tactic": "Execution", "mitre_technique": "User Execution: Malicious File", "mitre_id": "T1204.002"},
    {"title": "Anomalous Login Location — {user}", "description": "User {user} logged in from {country} ({src_ip}). Previous login was from India 2 hours ago. Impossible travel detected.", "severity": "medium", "source": "IAM", "mitre_tactic": "Initial Access", "mitre_technique": "Valid Accounts", "mitre_id": "T1078"},
    {"title": "Privilege Escalation Attempt — {host}", "description": "Process {proc} attempted to elevate privileges via {technique} on {host}.", "severity": "high", "source": "EDR", "mitre_tactic": "Privilege Escalation", "mitre_technique": "Exploitation for Privilege Escalation", "mitre_id": "T1068"},
    {"title": "Port Scan Detected — {src_ip}", "description": "Host {src_ip} scanning {port_count} ports on {dest_ip}. Detected SYN scan pattern across {subnet}.", "severity": "low", "source": "Firewall", "mitre_tactic": "Discovery", "mitre_technique": "Network Service Discovery", "mitre_id": "T1046"},
    {"title": "Suspicious PowerShell — {host}", "description": "Encoded PowerShell command detected: {cmd}. Process spawned by {parent}.", "severity": "high", "source": "EDR", "mitre_tactic": "Execution", "mitre_technique": "Command and Scripting Interpreter: PowerShell", "mitre_id": "T1059.001"},
    {"title": "Data Upload to Cloud Storage — {user}", "description": "User {user} uploaded {size}MB to external cloud storage ({service}) from {host}. Outside business hours.", "severity": "medium", "source": "SIEM", "mitre_tactic": "Exfiltration", "mitre_technique": "Exfiltration to Cloud Storage", "mitre_id": "T1567.002"},
    {"title": "Failed MFA Verification — {user}", "description": "{count} MFA push rejections for {user} from {src_ip}. Potential MFA fatigue attack.", "severity": "medium", "source": "IAM", "mitre_tactic": "Credential Access", "mitre_technique": "Multi-Factor Auth Request Generation", "mitre_id": "T1621"},
    {"title": "Lateral Movement via RDP — {host}", "description": "RDP session from {src_ip} to {host} using service account {user}. Account not typically used for interactive login.", "severity": "high", "source": "SIEM", "mitre_tactic": "Lateral Movement", "mitre_technique": "Remote Desktop Protocol", "mitre_id": "T1021.001"},
    {"title": "Crypto Mining Activity — {host}", "description": "CPU usage spike to 98% on {host}. Outbound connections to mining pool {pool} detected.", "severity": "medium", "source": "EDR", "mitre_tactic": "Impact", "mitre_technique": "Resource Hijacking", "mitre_id": "T1496"},
    {"title": "AWS IAM Key Exposed — {user}", "description": "AWS access key for {user} found in public GitHub repository. Key has S3 and EC2 permissions.", "severity": "critical", "source": "Cloud", "mitre_tactic": "Credential Access", "mitre_technique": "Unsecured Credentials", "mitre_id": "T1552"},
    {"title": "SQL Injection Attempt — {host}", "description": "WAF detected SQL injection payload in POST request to {endpoint} from {src_ip}. Pattern: {payload}", "severity": "high", "source": "SIEM", "mitre_tactic": "Initial Access", "mitre_technique": "Exploit Public-Facing Application", "mitre_id": "T1190"},
    {"title": "Scheduled Task Created — {host}", "description": "New scheduled task created on {host} by {user}. Task executes binary from temp directory.", "severity": "medium", "source": "EDR", "mitre_tactic": "Persistence", "mitre_technique": "Scheduled Task/Job", "mitre_id": "T1053"},
    {"title": "Firewall Rule Modification — {host}", "description": "Firewall rule added allowing inbound traffic on port {port} from 0.0.0.0/0 on {host}.", "severity": "medium", "source": "Firewall", "mitre_tactic": "Defense Evasion", "mitre_technique": "Impair Defenses", "mitre_id": "T1562.004"},
]

HOSTS = ["prod-web-01", "prod-web-02", "db-primary-01", "app-server-01", "ws-finance-03", "ws-hr-07", "ws-dev-12", "dc-primary-01", "file-server-01", "mail-gw-01", "vpn-gw-01", "k8s-node-01"]
USERS = ["j.smith", "a.williams", "r.chen", "k.patel", "m.jones", "s.kumar", "d.lee", "p.nguyen", "admin_svc", "svc_backup", "svc_api", "www-data"]
IPS = ["185.220.101.42", "45.33.32.156", "91.219.236.222", "198.51.100.23", "203.0.113.45", "23.227.38.64", "103.152.220.17", "45.154.255.139"]
DOMAINS = ["cdn-update.xyz", "api.auth-verify.cc", "d4ta-sync.top", "corp-vpn.club"]
COUNTRIES = ["Russia", "China", "North Korea", "Brazil", "Romania"]

def _generate_alert() -> dict:
    template = random.choice(TEMPLATES)
    host = random.choice(HOSTS)
    user = random.choice(USERS)
    src_ip = random.choice(IPS)
    dest_ip = f"10.0.{random.randint(1,5)}.{random.randint(10,250)}"
    fmt = {"host": host, "user": user, "src_ip": src_ip, "dest_ip": dest_ip,
           "count": random.randint(5, 200), "mins": random.randint(1, 30),
           "domain": random.choice(DOMAINS), "hash": uuid.uuid4().hex[:16],
           "filename": random.choice(["update.exe", "svchost.dll", "tmp.ps1"]),
           "country": random.choice(COUNTRIES), "proc": random.choice(["cmd.exe", "python.exe", "rundll32.exe"]),
           "technique": random.choice(["named pipe impersonation", "DLL injection", "token theft"]),
           "port_count": random.randint(100, 65000), "subnet": f"10.0.{random.randint(1,5)}.0/24",
           "cmd": "IEX(New-Object Net.WebClient).DownloadString(...)",
           "parent": random.choice(["WINWORD.EXE", "explorer.exe", "outlook.exe"]),
           "size": random.randint(50, 5000), "service": random.choice(["Dropbox", "Google Drive", "Mega.nz"]),
           "pool": "pool.minexmr.com", "port": random.choice([22, 3389, 4444, 8080]),
           "endpoint": random.choice(["/api/login", "/api/users", "/admin/config"]),
           "payload": "' OR 1=1--"}
    return {"title": template["title"].format(**fmt), "description": template["description"].format(**fmt),
            "severity": template["severity"], "source": template["source"],
            "mitre_tactic": template["mitre_tactic"], "mitre_technique": template["mitre_technique"],
            "mitre_id": template["mitre_id"], "source_ip": src_ip, "dest_ip": dest_ip,
            "hostname": host, "username": user, "is_synthetic": True, "created_at": datetime.now(timezone.utc)}

_running = False

async def auto_triage_existing():
    """Auto-triage all untriaged alerts on startup."""
    async with async_session() as db:
        from sqlalchemy import select
        result = await db.execute(select(Alert).where(Alert.ai_verdict.is_(None)))
        untriaged = result.scalars().all()
        for alert in untriaged:
            await triage_alert(alert, db)
        if untriaged:
            print(f"[Simulator] Auto-triaged {len(untriaged)} existing alerts")

async def start_simulator(interval_min: int = 25, interval_max: int = 45):
    global _running
    if _running:
        return
    _running = True
    # Auto-triage existing alerts first
    await auto_triage_existing()
    print(f"[Simulator] Started — generating alerts every {interval_min}-{interval_max}s")
    while _running:
        wait = random.randint(interval_min, interval_max)
        await asyncio.sleep(wait)
        try:
            async with async_session() as db:
                data = _generate_alert()
                alert = Alert(**data)
                apply_ocsf(alert)
                db.add(alert)
                await db.commit()
                await db.refresh(alert)
                # Auto-triage the new alert
                await triage_alert(alert, db)
                print(f"[Simulator] New alert: {alert.title} ({alert.severity}) → {alert.ai_verdict}")
        except Exception as e:
            print(f"[Simulator] Error: {e}")

def stop_simulator():
    global _running
    _running = False
