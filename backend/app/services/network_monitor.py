"""Real Network Monitor — watches live connections using lsof/netstat (no root needed)."""
import asyncio
import subprocess
import socket
import time
import re
from datetime import datetime, timezone
from collections import defaultdict
from app.database import async_session
from app.models import Alert
from app.services.ai_engine import triage_alert

SUSPICIOUS_PORTS = {4444, 4445, 5555, 6666, 6667, 6668, 6669, 7777, 8888, 9999,
                    1337, 31337, 12345, 54321, 1234, 3127, 27374, 65535}
KNOWN_PORTS = {80, 443, 8080, 8443, 53, 22, 993, 995, 587, 465, 143, 110, 25,
               3306, 5432, 5672, 6379, 27017, 3000, 8000, 8001, 9090, 5353, 631}

_alerted = set()
_conn_history = defaultdict(list)
_running = False


def _get_connections():
    """Parse lsof output to get active network connections."""
    try:
        result = subprocess.run(
            ["lsof", "-i", "-nP", "-sTCP:ESTABLISHED"],
            capture_output=True, text=True, timeout=10
        )
        connections = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) < 9:
                continue
            proc_name = parts[0]
            pid = parts[1]
            name_col = parts[8] if len(parts) >= 9 else ""
            # Parse "10.0.0.1:443->142.250.1.1:https" format
            match = re.search(r'([\d.]+):(\d+)->([\d.]+):(\d+)', name_col)
            if not match:
                # Try without port resolution
                match = re.search(r'([\d.]+):(\w+)->([\d.]+):(\w+)', name_col)
            if match:
                local_ip, local_port, remote_ip, remote_port = match.groups()
                try:
                    remote_port = int(remote_port)
                except ValueError:
                    try:
                        remote_port = socket.getservbyname(remote_port)
                    except Exception:
                        continue
                try:
                    local_port = int(local_port)
                except ValueError:
                    local_port = 0
                connections.append({
                    "proc": proc_name, "pid": pid,
                    "local_ip": local_ip, "local_port": local_port,
                    "remote_ip": remote_ip, "remote_port": remote_port,
                })
        return connections
    except Exception as e:
        print(f"[NetworkMonitor] lsof error: {e}")
        return []


def _is_private(ip):
    try:
        p = ip.split(".")
        f, s = int(p[0]), int(p[1])
        return f == 10 or (f == 172 and 16 <= s <= 31) or (f == 192 and s == 168) or f == 127 or f == 0
    except Exception:
        return True


def scan_network():
    """Scan and detect suspicious patterns from real network traffic."""
    alerts = []
    connections = _get_connections()
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    external = [c for c in connections if not _is_private(c["remote_ip"])]
    ip_conns = defaultdict(list)
    proc_conns = defaultdict(list)

    for c in external:
        ip_conns[c["remote_ip"]].append(c)
        proc_conns[c["proc"]].append(c)
        _conn_history[c["remote_ip"]].append(time.time())
        _conn_history[c["remote_ip"]] = [t for t in _conn_history[c["remote_ip"]] if time.time() - t < 300]

        key = f"{c['remote_ip']}:{c['remote_port']}:{c['proc']}"

        # 1. Suspicious port
        if c["remote_port"] in SUSPICIOUS_PORTS and key not in _alerted:
            _alerted.add(key)
            alerts.append({
                "title": f"Suspicious Port Connection — {c['proc']}",
                "description": f"Process '{c['proc']}' (PID {c['pid']}) connected to {c['remote_ip']}:{c['remote_port']}. "
                               f"Port {c['remote_port']} is associated with known malware/C2 backdoors.",
                "severity": "high", "source": "Network Monitor",
                "mitre_tactic": "Command and Control", "mitre_technique": "Non-Standard Port",
                "mitre_id": "T1571", "source_ip": local_ip, "dest_ip": c["remote_ip"],
                "hostname": hostname, "username": c["proc"],
            })

        # 2. Non-standard high port
        if c["remote_port"] > 10000 and c["remote_port"] not in KNOWN_PORTS and c["remote_port"] not in SUSPICIOUS_PORTS:
            hkey = f"high:{c['remote_ip']}:{c['remote_port']}:{c['proc']}"
            if hkey not in _alerted:
                _alerted.add(hkey)
                alerts.append({
                    "title": f"Non-Standard Port Activity — {c['proc']}",
                    "description": f"'{c['proc']}' connected to {c['remote_ip']} on port {c['remote_port']}. "
                                   f"Non-standard ports may indicate tunneling or C2.",
                    "severity": "low", "source": "Network Monitor",
                    "mitre_tactic": "Command and Control", "mitre_technique": "Non-Standard Port",
                    "mitre_id": "T1571", "source_ip": local_ip, "dest_ip": c["remote_ip"],
                    "hostname": hostname, "username": c["proc"],
                })

    # 3. High frequency to same IP
    for ip, ts in _conn_history.items():
        if len(ts) >= 10:
            fkey = f"freq:{ip}"
            if fkey not in _alerted:
                _alerted.add(fkey)
                cc = ip_conns.get(ip, [{}])
                alerts.append({
                    "title": f"Beaconing Activity — {ip}",
                    "description": f"{len(ts)} connections to {ip} in 5 minutes via '{cc[0].get('proc','unknown')}'. "
                                   f"Repeated connections may indicate C2 beaconing.",
                    "severity": "medium", "source": "Network Monitor",
                    "mitre_tactic": "Command and Control", "mitre_technique": "Application Layer Protocol",
                    "mitre_id": "T1071", "source_ip": local_ip, "dest_ip": ip,
                    "hostname": hostname, "username": cc[0].get("proc", "unknown"),
                })

    # 4. Process with many unique destinations
    for proc, conns in proc_conns.items():
        unique = set(c["remote_ip"] for c in conns)
        if len(unique) >= 15:
            skey = f"scatter:{proc}"
            if skey not in _alerted:
                _alerted.add(skey)
                alerts.append({
                    "title": f"Excessive Outbound Connections — {proc}",
                    "description": f"'{proc}' connected to {len(unique)} unique external IPs. "
                                   f"May indicate scanning or distributed C2.",
                    "severity": "medium", "source": "Network Monitor",
                    "mitre_tactic": "Discovery", "mitre_technique": "Network Service Discovery",
                    "mitre_id": "T1046", "source_ip": local_ip, "dest_ip": "multiple",
                    "hostname": hostname, "username": proc,
                })

    # 5. Activity summary every 2 minutes
    if external:
        akey = f"summary:{int(time.time()) // 120}"
        if akey not in _alerted:
            _alerted.add(akey)
            unique_ips = len(ip_conns)
            top = sorted(ip_conns.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            top_str = ", ".join(f"{ip}({len(c)} via {c[0]['proc']})" for ip, c in top)
            alerts.append({
                "title": f"Live Network Snapshot — {len(external)} external connections",
                "description": f"Active: {len(external)} connections to {unique_ips} unique external IPs. "
                               f"Top: {top_str}",
                "severity": "info", "source": "Network Monitor",
                "mitre_tactic": "Discovery", "mitre_technique": "System Network Connections Discovery",
                "mitre_id": "T1049", "source_ip": local_ip, "dest_ip": "multiple",
                "hostname": hostname, "username": "system",
            })

    return alerts


async def start_network_monitor(interval: int = 15):
    global _running
    if _running:
        return
    _running = True
    print(f"[NetworkMonitor] Started — scanning every {interval}s")
    while _running:
        try:
            alerts_data = scan_network()
            if alerts_data:
                async with async_session() as db:
                    for data in alerts_data:
                        alert = Alert(**data, is_synthetic=False, created_at=datetime.now(timezone.utc))
                        db.add(alert)
                        await db.commit()
                        await db.refresh(alert)
                        await triage_alert(alert, db)
                        print(f"[NetworkMonitor] REAL: {alert.title} ({alert.severity}) -> {alert.ai_verdict}")
        except Exception as e:
            print(f"[NetworkMonitor] Error: {e}")
        await asyncio.sleep(interval)


def stop_network_monitor():
    global _running
    _running = False
