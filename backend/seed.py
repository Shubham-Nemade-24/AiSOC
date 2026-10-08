"""Seed the database with 20 realistic security alerts."""
import asyncio
import random
from datetime import datetime, timezone, timedelta
from app.database import init_db, async_session
from app.models import Alert

ALERTS = [
    {"title": "Brute Force SSH Login Attempt", "description": "Multiple failed SSH login attempts detected from external IP targeting production server. 47 failed attempts in 5 minutes from single source.", "severity": "high", "source": "EDR", "mitre_tactic": "Credential Access", "mitre_technique": "Brute Force", "mitre_id": "T1110", "source_ip": "185.220.101.42", "dest_ip": "10.0.1.15", "hostname": "prod-web-01", "username": "root"},
    {"title": "Suspicious PowerShell Execution", "description": "Encoded PowerShell command detected executing base64 payload with bypass execution policy. Process spawned from Word document.", "severity": "critical", "source": "EDR", "mitre_tactic": "Execution", "mitre_technique": "PowerShell", "mitre_id": "T1059.001", "source_ip": "10.0.2.34", "dest_ip": "10.0.2.34", "hostname": "ws-finance-03", "username": "j.smith"},
    {"title": "Data Exfiltration via DNS", "description": "Unusually large DNS TXT queries detected to suspicious domain. Potential data exfiltration through DNS tunneling. 500MB transferred in 2 hours.", "severity": "critical", "source": "Firewall", "mitre_tactic": "Exfiltration", "mitre_technique": "Exfiltration Over Alternative Protocol", "mitre_id": "T1048", "source_ip": "10.0.3.22", "dest_ip": "45.33.32.156", "hostname": "db-staging-01", "username": "svc_backup"},
    {"title": "Lateral Movement via SMB", "description": "SMB connection from compromised workstation to multiple internal servers using harvested credentials. PsExec activity detected.", "severity": "high", "source": "SIEM", "mitre_tactic": "Lateral Movement", "mitre_technique": "Remote Services: SMB", "mitre_id": "T1021.002", "source_ip": "10.0.2.34", "dest_ip": "10.0.1.50", "hostname": "ws-finance-03", "username": "admin_svc"},
    {"title": "Ransomware File Encryption", "description": "Rapid file rename operations detected with known ransomware extension (.locked). 1,200 files affected in shared drive within 3 minutes.", "severity": "critical", "source": "EDR", "mitre_tactic": "Impact", "mitre_technique": "Data Encrypted for Impact", "mitre_id": "T1486", "source_ip": "10.0.4.12", "dest_ip": "10.0.1.100", "hostname": "file-server-01", "username": "m.jones"},
    {"title": "Privilege Escalation via Token Manipulation", "description": "Process token impersonation detected. Low-privilege service account elevated to SYSTEM privileges on domain controller.", "severity": "critical", "source": "EDR", "mitre_tactic": "Privilege Escalation", "mitre_technique": "Access Token Manipulation", "mitre_id": "T1134", "source_ip": "10.0.1.5", "dest_ip": "10.0.1.5", "hostname": "dc-primary-01", "username": "svc_monitor"},
    {"title": "Phishing Email with Malicious Attachment", "description": "Email with macro-enabled Word document detected. Sender domain typosquatting legitimate vendor. 12 recipients in finance department.", "severity": "high", "source": "Email", "mitre_tactic": "Initial Access", "mitre_technique": "Phishing: Spearphishing Attachment", "mitre_id": "T1566.001", "source_ip": "198.51.100.23", "dest_ip": "10.0.5.10", "hostname": "mail-gw-01", "username": "multiple"},
    {"title": "Unauthorized AWS S3 Bucket Access", "description": "API calls from unrecognized IP accessing S3 bucket containing customer PII. Access key potentially compromised.", "severity": "high", "source": "Cloud", "mitre_tactic": "Collection", "mitre_technique": "Data from Cloud Storage", "mitre_id": "T1530", "source_ip": "203.0.113.45", "dest_ip": "N/A", "hostname": "aws-prod", "username": "iam_deploy_svc"},
    {"title": "Suspicious Cron Job Creation", "description": "New crontab entry created on production Linux server scheduling outbound connection every 15 minutes to external C2 server.", "severity": "medium", "source": "EDR", "mitre_tactic": "Persistence", "mitre_technique": "Scheduled Task/Job: Cron", "mitre_id": "T1053.003", "source_ip": "10.0.1.20", "dest_ip": "91.219.236.222", "hostname": "app-server-02", "username": "www-data"},
    {"title": "MFA Bypass Attempt", "description": "Multiple MFA push notifications sent to single user account. Possible MFA fatigue attack. 23 push attempts in 10 minutes.", "severity": "medium", "source": "IAM", "mitre_tactic": "Credential Access", "mitre_technique": "Multi-Factor Auth Request Generation", "mitre_id": "T1621", "source_ip": "198.51.100.88", "dest_ip": "N/A", "hostname": "okta-prod", "username": "a.williams"},
    {"title": "Mimikatz Detection on Workstation", "description": "Known credential dumping tool Mimikatz detected in memory. LSASS process access from unsigned binary.", "severity": "critical", "source": "EDR", "mitre_tactic": "Credential Access", "mitre_technique": "OS Credential Dumping: LSASS Memory", "mitre_id": "T1003.001", "source_ip": "10.0.2.55", "dest_ip": "10.0.2.55", "hostname": "ws-hr-07", "username": "r.chen"},
    {"title": "Abnormal Database Query Volume", "description": "Service account executing 10x normal query volume against customer database. 50,000 SELECT queries in 30 minutes.", "severity": "medium", "source": "SIEM", "mitre_tactic": "Collection", "mitre_technique": "Data from Information Repositories", "mitre_id": "T1213", "source_ip": "10.0.3.15", "dest_ip": "10.0.1.100", "hostname": "api-server-01", "username": "svc_api"},
    {"title": "Outbound Connection to Known C2 Server", "description": "Network connection established to IP listed in threat intelligence feed as Cobalt Strike C2 infrastructure.", "severity": "high", "source": "Firewall", "mitre_tactic": "Command and Control", "mitre_technique": "Application Layer Protocol", "mitre_id": "T1071", "source_ip": "10.0.4.33", "dest_ip": "23.227.38.64", "hostname": "ws-dev-12", "username": "k.patel"},
    {"title": "Registry Persistence Mechanism", "description": "New Run key added to Windows registry pointing to suspicious executable in temp directory.", "severity": "medium", "source": "EDR", "mitre_tactic": "Persistence", "mitre_technique": "Boot or Logon Autostart: Registry Run Keys", "mitre_id": "T1547.001", "source_ip": "10.0.2.41", "dest_ip": "10.0.2.41", "hostname": "ws-sales-05", "username": "t.garcia"},
    {"title": "Suspicious VPN Login from Unusual Location", "description": "VPN authentication from IP geolocated to country not in employee travel records. Same user logged in from home office 2 hours prior.", "severity": "medium", "source": "IAM", "mitre_tactic": "Initial Access", "mitre_technique": "Valid Accounts", "mitre_id": "T1078", "source_ip": "103.152.220.17", "dest_ip": "10.0.0.1", "hostname": "vpn-gw-01", "username": "s.kumar"},
    {"title": "Web Shell Detected on Server", "description": "PHP web shell uploaded to public-facing web server. File created in uploads directory with eval() and system() calls.", "severity": "critical", "source": "EDR", "mitre_tactic": "Persistence", "mitre_technique": "Server Software Component: Web Shell", "mitre_id": "T1505.003", "source_ip": "45.154.255.139", "dest_ip": "10.0.1.30", "hostname": "web-public-01", "username": "www-data"},
    {"title": "Kerberoasting Activity Detected", "description": "Service ticket requests for multiple service accounts from single workstation. Potential offline password cracking attempt.", "severity": "high", "source": "SIEM", "mitre_tactic": "Credential Access", "mitre_technique": "Steal or Forge Kerberos Tickets: Kerberoasting", "mitre_id": "T1558.003", "source_ip": "10.0.2.44", "dest_ip": "10.0.1.5", "hostname": "ws-it-admin-01", "username": "p.nguyen"},
    {"title": "Cloud IAM Policy Modification", "description": "IAM policy changed to grant AdministratorAccess to newly created user account outside of change window.", "severity": "high", "source": "Cloud", "mitre_tactic": "Persistence", "mitre_technique": "Account Manipulation", "mitre_id": "T1098", "source_ip": "N/A", "dest_ip": "N/A", "hostname": "aws-prod", "username": "terraform_ci"},
    {"title": "Network Scan from Internal Host", "description": "Port scanning activity detected from internal workstation targeting entire /24 subnet. 254 hosts scanned on ports 22, 80, 443, 3389.", "severity": "low", "source": "Firewall", "mitre_tactic": "Discovery", "mitre_technique": "Network Service Discovery", "mitre_id": "T1046", "source_ip": "10.0.2.60", "dest_ip": "10.0.1.0/24", "hostname": "ws-dev-08", "username": "d.lee"},
    {"title": "Failed Login Spike on Web Application", "description": "300% increase in failed login attempts on customer-facing web application. Distributed across 50+ source IPs suggesting credential stuffing.", "severity": "medium", "source": "SIEM", "mitre_tactic": "Credential Access", "mitre_technique": "Brute Force: Credential Stuffing", "mitre_id": "T1110.004", "source_ip": "multiple", "dest_ip": "10.0.1.35", "hostname": "app-web-01", "username": "multiple"},
]


async def seed():
    await init_db()
    async with async_session() as db:
        existing = (await db.execute(__import__('sqlalchemy').select(__import__('sqlalchemy').func.count(Alert.id)))).scalar()
        if existing and existing > 0:
            print(f"Database already has {existing} alerts. Skipping seed.")
            return
        now = datetime.now(timezone.utc)
        for i, data in enumerate(ALERTS):
            alert = Alert(
                **data,
                is_synthetic=True,
                created_at=now - timedelta(hours=random.randint(1, 480)),
            )
            db.add(alert)
        await db.commit()
        print(f"Seeded {len(ALERTS)} alerts successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
