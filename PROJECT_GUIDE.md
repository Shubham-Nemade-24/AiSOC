# AiSOC — Complete Project Guide
### AI-Driven Security Operations Center
**Gen AI Capstone Project | Group 4 | PCCOE Pune**
**Shubham Nemade · Anushka Somawanshi · Atharva Karale**
**Guide: Prof. Santwana Ingole | Dept of CSE (AI & ML) | 2026-2027**

---

## Table of Contents
1. [What is AiSOC?](#1-what-is-aisoc)
2. [Problem Statement](#2-problem-statement)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Project Structure](#5-project-structure)
6. [Backend — Detailed Code Walkthrough](#6-backend--detailed-code-walkthrough)
7. [Frontend — Detailed Code Walkthrough](#7-frontend--detailed-code-walkthrough)
8. [Data Flow — End to End](#8-data-flow--end-to-end)
9. [Key Features Explained](#9-key-features-explained)
10. [API Endpoints](#10-api-endpoints)
11. [How to Run](#11-how-to-run)
12. [Synopsis Mapping](#12-synopsis-mapping)

---

## 1. What is AiSOC?

AiSOC (AI-driven Security Operations Center) is a full-stack web application that uses **Google Gemini** (Generative AI) to automate cybersecurity alert triage, investigation, and response recommendation.

In a real SOC, human analysts manually review hundreds of security alerts daily — most of which are false positives. AiSOC automates this with:
- **AI-powered triage** — Gemini classifies alerts as true_positive, false_positive, suspicious, or benign
- **Multi-agent investigation** — 4 specialized AI agents analyze each alert step-by-step
- **Immutable audit trail** — Every AI decision is logged with SHA-256 hashes for accountability
- **Real-time monitoring** — Scans your actual network traffic for threats
- **Privacy protection** — Sensitive data is pseudonymized before being sent to the AI

---

## 2. Problem Statement

Modern organizations face 3 critical cybersecurity challenges:

1. **Alert Fatigue**: SOCs receive 10,000+ alerts/day. 85% are false positives. Analysts burn out triaging noise.
2. **Slow Investigation**: Manual investigation of a single alert takes 30-60 minutes. Attackers move in seconds.
3. **No AI Accountability**: When AI makes security decisions, there's no audit trail. Regulators need traceability.

**AiSOC solves all three:**
- AI reduces alert noise by 40-60% via automated triage
- Multi-agent pipeline investigates alerts in seconds, not hours
- Investigation Ledger provides SHA-256-hashed, tamper-evident audit trail

---

## 3. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js 14)                        │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐ ┌────────────┐  │
│  │Dashboard │ │ Alerts   │ │ Investigations │ │ Evaluation │  │
│  │ (live)   │ │ (live)   │ │ (ledger view)  │ │ (metrics)  │  │
│  └──────────┘ └──────────┘ └────────────────┘ └────────────┘  │
│                    ↕ HTTP REST API (port 3000 → 8000)          │
└────────────────────────────────────────────────────────────────┘
                              ↕
┌────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              INGESTION LAYER                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │  Network    │  │   Alert      │  │     OCSF       │  │  │
│  │  │  Monitor    │  │  Simulator   │  │  Normalizer    │  │  │
│  │  │ (real lsof) │  │ (synthetic)  │  │  (standards)   │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │  │
│  └─────────┼────────────────┼──────────────────┼────────────┘  │
│            └────────────────┼──────────────────┘               │
│                             ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           CORRELATION ENGINE                              │  │
│  │  Groups alerts by shared IPs, hostnames, users           │  │
│  │  within 60-minute time windows                           │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          PSEUDONYMIZATION MODULE                          │  │
│  │  IP → [IP_001], hostname → [HOST_001], etc.              │  │
│  │  Reversible mapping stored in memory                     │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        MULTI-AGENT INVESTIGATION PIPELINE                 │  │
│  │  ┌─────────┐  ┌────────────┐  ┌──────────┐  ┌────────┐  │  │
│  │  │ Triage  │→ │ Enrichment │→ │ Forensic │→ │Response│  │  │
│  │  │  Agent  │  │   Agent    │  │  Agent   │  │ Agent  │  │  │
│  │  └─────────┘  └────────────┘  └──────────┘  └────────┘  │  │
│  │                    ↓ each step                            │  │
│  │         Investigation Ledger (SHA-256 chain)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLite DATABASE                               │  │
│  │  alerts │ investigations │ ledger_entries                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- **Monorepo**: Backend and frontend in one repository for easy deployment
- **SQLite**: Zero-config database — no Docker, no PostgreSQL install needed
- **Async**: All database operations are async for performance (aiosqlite)
- **Auto-reload**: Backend uses uvicorn's `--reload` flag for development

---

## 4. Tech Stack

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Frontend** | Next.js 14 (React) | Server-side rendering, file-based routing, production-ready |
| **Styling** | Tailwind CSS | Utility-first, rapid prototyping, dark theme |
| **Charts** | Recharts | React-native charting library, composable |
| **Backend** | FastAPI (Python) | Async, auto-generated API docs, type-safe |
| **ORM** | SQLAlchemy 2.0 | Async support, declarative models, migration-ready |
| **Database** | SQLite + aiosqlite | Zero config, file-based, perfect for demo |
| **AI** | Google Gemini 1.5 Flash | Free tier, fast, good for security analysis |
| **Privacy** | Custom pseudonymizer | Regex-based, reversible, no external deps |
| **Integrity** | hashlib SHA-256 | Python standard library, cryptographic |

---

## 5. Project Structure

```
OUR_AiSOC/
├── .env.example                    # Environment variables template
├── .env                            # Your actual API key (git-ignored)
├── README.md                       # Project documentation
├── run.txt                         # Quick-start commands
├── PROJECT_GUIDE.md                # This guide
│
├── backend/                        # Python FastAPI backend
│   ├── requirements.txt            # pip dependencies (7 packages)
│   ├── seed.py                     # Seeds 20 realistic alerts
│   ├── aisoc.db                    # SQLite database (auto-created)
│   └── app/
│       ├── __init__.py
│       ├── database.py             # Database connection & session
│       ├── main.py                 # FastAPI app entry point
│       ├── models.py               # ORM models (3 tables)
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── alerts.py           # Alert CRUD + triage + investigate
│       │   ├── dashboard.py        # Metrics + evaluation + correlations
│       │   └── investigations.py   # Investigation listing + ledger
│       └── services/
│           ├── __init__.py
│           ├── ai_engine.py        # Gemini AI triage + multi-agent pipeline
│           ├── pseudonymizer.py    # Data masking before LLM
│           ├── correlation.py      # Alert grouping engine
│           ├── network_monitor.py  # Real network traffic scanner
│           └── simulator.py        # Synthetic alert generator
│
└── frontend/                       # Next.js 14 frontend
    ├── package.json                # npm dependencies
    ├── next.config.mjs             # API proxy configuration
    ├── tailwind.config.ts          # Theme configuration
    ├── tsconfig.json               # TypeScript config
    └── src/
        ├── app/
        │   ├── layout.tsx          # Root layout (sidebar + main area)
        │   ├── globals.css         # Global styles & animations
        │   ├── page.tsx            # Dashboard page
        │   ├── alerts/
        │   │   ├── page.tsx        # Alerts list page
        │   │   └── [id]/page.tsx   # Alert detail + investigation
        │   ├── investigations/
        │   │   └── page.tsx        # Investigation history
        │   └── evaluation/
        │       └── page.tsx        # Evaluation metrics
        ├── components/
        │   └── Sidebar.tsx         # Navigation sidebar
        └── lib/
            └── api.ts              # API client functions
```

---

## 6. Backend — Detailed Code Walkthrough

### 6.1 database.py (24 lines) — Database Setup

This file configures SQLAlchemy to use **async SQLite**.

**How it works:**
- `create_async_engine()` creates an async database connection to `aisoc.db`
- `async_sessionmaker()` creates reusable database session factories
- `get_db()` is a FastAPI dependency — every API endpoint gets a fresh database session
- `init_db()` creates all tables on first run using `Base.metadata.create_all`

**Key concept:** We use `aiosqlite` driver so database queries don't block the event loop. This means the server can handle multiple requests simultaneously.

---

### 6.2 models.py (150 lines) — Database Schema

Defines 3 database tables using SQLAlchemy ORM:

**Table 1: `alerts`** — Security events
```
id              UUID string (primary key)
title           Alert headline (e.g., "Brute Force SSH Login")
description     Detailed description
severity        critical / high / medium / low / info
status          new / triaged / investigating / resolved / closed
source          EDR / SIEM / Firewall / IAM / Cloud / Network Monitor

# MITRE ATT&CK mapping
mitre_tactic    e.g., "Credential Access"
mitre_technique e.g., "Brute Force"
mitre_id        e.g., "T1110"

# Network observables
source_ip       Attacker IP
dest_ip         Target IP
hostname        Affected machine
username        Affected user

# OCSF Schema Fields (Open Cybersecurity Schema Framework)
ocsf_class_uid     Event class (2001=Security Finding, 4001=Network Activity)
ocsf_category_uid  Category (2=Findings)
ocsf_severity_id   1(Info) to 5(Critical)
ocsf_type_uid      Full type identifier (class*100 + activity)

# AI triage results
ai_verdict      true_positive / false_positive / suspicious / benign
ai_confidence   0.0 to 1.0
ai_reasoning    AI's explanation for the verdict
ai_priority     1 to 10

correlation_group  UUID linking correlated alerts
```

**Table 2: `investigations`** — AI investigation results
```
id              UUID
alert_id        Foreign key → alerts
status          running / completed
summary         AI-generated summary
recommendation  Response recommendation
risk_score      0.0 to 10.0
```

**Table 3: `ledger_entries`** — Immutable audit trail
```
id                UUID
investigation_id  Foreign key → investigations
step_number       1, 2, 3, 4
agent_name        triage_agent / enrichment_agent / forensic_agent / response_agent
action            What the agent did
input_summary     What was sent to the agent
output_summary    What the agent produced
confidence        0.0 to 1.0
model_used        "gemini-1.5-flash" or "rule-based"
tokens_used       LLM token count
duration_ms       Processing time

# SHA-256 integrity chain
content_hash      SHA-256 hash of THIS entry's content
prev_hash         SHA-256 hash of PREVIOUS entry (creates chain)
pseudonymized     True/False — was data masked before LLM?
```

**OCSF Helper Function:**
`apply_ocsf(alert)` maps our severity and source to standard OCSF fields. For example:
- `severity="critical"` → `ocsf_severity_id=5`
- `source="EDR"` → `ocsf_class_uid=2001` (Security Finding)
- `source="Firewall"` → `ocsf_class_uid=4001` (Network Activity)

**SHA-256 Hash Chain:**
`LedgerEntry.compute_hash(prev_hash)` creates a tamper-evident chain:
1. Serializes entry fields to JSON
2. Includes the previous entry's hash
3. Computes SHA-256 of the combined payload
4. If anyone modifies a past entry, all subsequent hashes break

---

### 6.3 main.py (68 lines) — Application Entry Point

This is where the FastAPI application starts.

**Lifespan Management:**
```python
@asynccontextmanager
async def lifespan(app):
    await init_db()                              # Create tables
    tasks = [
        asyncio.create_task(start_simulator()),    # Synthetic alerts
        asyncio.create_task(start_network_monitor()), # Real network scan
        asyncio.create_task(start_correlation_engine()), # Alert grouping
    ]
    yield                                        # App runs here
    # Cleanup on shutdown
    stop_simulator()
    stop_network_monitor()
    stop_correlation_engine()
```

When the server starts, 3 background tasks launch automatically:
1. **Simulator** — generates a new synthetic alert every 30-50 seconds
2. **Network Monitor** — scans real network connections every 15 seconds
3. **Correlation Engine** — groups related alerts every 60 seconds

**CORS Middleware:**
Allows the frontend (port 3000) to call the backend (port 8000) without browser blocking.

**Route Registration:**
3 routers are included:
- `/api/alerts` — Alert management
- `/api/dashboard` — Metrics and evaluation
- `/api/investigations` — Investigation history

---

### 6.4 ai_engine.py (211 lines) — The AI Brain

This is the **core of the project** — the Gen AI component.

#### Function 1: `triage_alert(alert, db)` — AI Triage

**Step-by-step process:**
1. Create a `Pseudonymizer` instance
2. Check if Gemini API key is configured
3. If no key → use `_fallback_triage()` (rule-based, works without internet)
4. If key exists:
   a. **Pseudonymize** sensitive fields (IPs, hostnames, usernames)
   b. Build a **prompt** asking Gemini to classify the alert
   c. Send to Gemini API, get response
   d. Parse JSON response (verdict, confidence, priority, reasoning)
   e. **Depseudonymize** the reasoning (restore real values)
   f. Save results to the alert record

**The Gemini Prompt:**
```
You are a SOC analyst AI. Triage this security alert and respond in JSON only.

Alert: Brute Force SSH Login Attempt
Description: 47 failed login attempts from [IP_001] targeting [HOST_001]
Severity: high
Source: EDR
MITRE: Credential Access / Brute Force
Source IP: [IP_001]
Hostname: [HOST_001]

Respond ONLY with this JSON:
{"verdict": "true_positive|false_positive|suspicious|benign",
 "confidence": 0.0-1.0, "priority": 1-10, "reasoning": "..."}
```

Notice how `185.220.101.42` becomes `[IP_001]` — this is pseudonymization at work.

**Fallback Triage (no API key):**
Uses severity-based rules:
- critical → true_positive (0.9 confidence)
- high → suspicious (0.75)
- medium → suspicious (0.6)
- low → benign (0.5)

#### Function 2: `investigate_alert(alert, db)` — Multi-Agent Pipeline

This runs 4 AI agents sequentially:

**Agent 1: Triage Agent** → Classifies the alert type and urgency
**Agent 2: Enrichment Agent** → Analyzes IOCs (IPs, domains, hashes)
**Agent 3: Forensic Agent** → Maps attack patterns to MITRE ATT&CK
**Agent 4: Response Agent** → Recommends containment actions

**For each agent:**
1. Pseudonymize the input
2. Send to Gemini with agent-specific prompt
3. Depseudonymize the output
4. Create a `LedgerEntry` with:
   - The input/output
   - Confidence score
   - Token count and duration
   - SHA-256 hash linking to previous entry
5. Save to database

**Final step:** Gemini summarizes all 4 agents' findings into a concise investigation report.

---

### 6.5 pseudonymizer.py (76 lines) — Privacy Module

**Why it matters:** When you send alert data to Google Gemini, you're sending real IP addresses, hostnames, and usernames to an external cloud API. This violates data sovereignty. The pseudonymizer masks all sensitive values before the LLM call.

**How it works:**
```python
pseudo = Pseudonymizer()
text = "Failed login from 192.168.1.100 on prod-web-01 by j.smith"
safe = pseudo.pseudonymize(text)
# → "Failed login from [IP_001] on [HOST_001] by [USER_001]"

# After LLM responds, restore real values:
restored = pseudo.depseudonymize(response)
```

**What gets masked:**
- Private IPs (10.x.x.x, 192.168.x.x, 172.16-31.x.x) → `[IP_001]`
- Hostnames (prod-web-01, dc-primary-01) → `[HOST_001]`
- Usernames (j.smith, admin_svc) → `[USER_001]`
- Emails → `[EMAIL_001]`
- File paths (/home/user/...) → `[PATH_001]`

**Reversible:** The mapping is stored in a dictionary. After the LLM responds, we replace tokens back with real values. The mapping is also logged for audit purposes.

---

### 6.6 correlation.py (135 lines) — Alert Fusion Engine

**Purpose:** Groups related alerts that share common entities.

**How it works:**
1. Fetch all alerts from the last 60 minutes
2. Extract entities from each alert:
   - `ip:185.220.101.42`
   - `host:prod-web-01`
   - `user:j.smith`
3. Build an entity → alert mapping
4. Find clusters: alerts sharing 2+ entities
5. Expand clusters transitively (if A shares an IP with B, and B shares a host with C, then A-B-C form one group)
6. Return cluster info: shared entities, severity, MITRE tactics, time span

**Example:** If these 3 alerts share `host:ws-finance-03`:
- "Suspicious PowerShell Execution" on ws-finance-03
- "Lateral Movement via SMB" from ws-finance-03
- "Mimikatz Detection" on ws-finance-03

They get correlated into one group → suggests a coordinated attack campaign.

---

### 6.7 network_monitor.py (210 lines) — Real Network Scanner

**This is the "real-time" component** — it monitors YOUR actual network connections.

**How it works:**
1. Runs `lsof -i -nP -sTCP:ESTABLISHED` (macOS command)
2. Parses the output to extract:
   - Process name (Chrome, python, ssh)
   - Remote IP and port
   - Local port
3. Filters out private/internal IPs
4. Applies detection rules:

**Detection Rule 1: Suspicious Port**
If any process connects to port 4444, 6666, 31337, etc. (known malware ports) → HIGH alert

**Detection Rule 2: Non-Standard High Port**
Connections to ports >10000 that aren't known services → LOW alert

**Detection Rule 3: Beaconing**
If 10+ connections to the same IP within 5 minutes → MEDIUM alert (C2 polling pattern)

**Detection Rule 4: Excessive Connections**
If one process has 15+ unique external IPs → MEDIUM alert (scanning behavior)

**Detection Rule 5: Activity Summary**
Every 2 minutes, logs a snapshot of all external connections → INFO alert

Each detected alert is:
- Saved to the database with `is_synthetic=False` (marking it as REAL)
- Auto-triaged by the AI engine
- Visible on the dashboard immediately

---

### 6.8 simulator.py (99 lines) — Synthetic Alert Generator

**Purpose:** Generates realistic-looking security alerts for demo purposes.

Contains 15 alert templates covering:
- Brute Force Login, Suspicious DNS, Malware Hash Match
- Anomalous Login Location, Privilege Escalation
- Port Scan, Suspicious PowerShell, Data Upload
- MFA Fatigue, Lateral Movement via RDP
- Crypto Mining, AWS Key Exposed, SQL Injection
- Scheduled Task, Firewall Rule Modification

Each template randomizes:
- Target hostname (from 12 realistic server names)
- Username (from 12 realistic user accounts)
- Source IP (from 8 known-malicious IPs)
- Attack parameters (count, port, domain, etc.)

**On startup:** Auto-triages all existing untriaged alerts.
**Every 30-50 seconds:** Generates one new alert → OCSF normalizes → auto-triages → saves.

---

### 6.9 routes/alerts.py (89 lines) — Alert API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/alerts` | GET | List all alerts (filter by severity/status) |
| `/api/alerts/{id}` | GET | Get single alert details |
| `/api/alerts/{id}/triage` | POST | Run AI triage on alert |
| `/api/alerts/{id}/investigate` | POST | Run full 4-agent investigation |
| `/api/alerts/{id}/status` | PATCH | Update alert status |

---

### 6.10 routes/dashboard.py (110 lines) — Dashboard & Evaluation API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/dashboard` | GET | Aggregate metrics (totals, by severity, by source, by status) |
| `/api/dashboard/evaluation` | GET | Evaluation harness (triage rate, reduction rate, confidence, ledger integrity) |
| `/api/dashboard/correlations` | GET | Alert correlation groups |

**Evaluation Metrics Explained:**
- **Triage Rate** = triaged alerts / total alerts × 100
- **Alert Reduction Rate** = (false_positives + benign) / triaged × 100 — measures noise removal
- **Avg Confidence** = average of all ai_confidence values
- **Hash Coverage** = entries with SHA-256 hash / total entries × 100

---

### 6.11 routes/investigations.py (60 lines) — Investigation API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/investigations` | GET | List all investigations with alert context |
| `/api/investigations/{id}` | GET | Full investigation with ledger entries |
| `/api/investigations/ledger/all` | GET | Raw ledger entries (last 100) |

---

### 6.12 seed.py (50 lines) — Database Seeder

Seeds 20 handcrafted security alerts covering diverse attack scenarios:
1. Brute Force SSH Login
2. Suspicious PowerShell Execution
3. Data Exfiltration via DNS
4. Lateral Movement via SMB
5. Ransomware File Encryption
6. Privilege Escalation via Token Manipulation
7. Phishing Email with Malicious Attachment
8. Unauthorized AWS S3 Access
9. Suspicious Cron Job
10. MFA Bypass Attempt
... and 10 more.

Each alert is OCSF-normalized via `apply_ocsf()` and timestamped to different hours (simulating alerts arriving over 20 days).

---

## 7. Frontend — Detailed Code Walkthrough

### 7.1 layout.tsx — Root Layout

Every page renders inside this layout:
- `<Sidebar />` — fixed 272px left panel
- `<main>` — content area with left margin

### 7.2 Sidebar.tsx — Navigation

4 navigation links with active state detection:
- Dashboard, Alerts, Investigations, Evaluation
- Shows active modules (OCSF, SHA-256, Pseudonymize, etc.)
- Displays team info at bottom

### 7.3 page.tsx (Dashboard) — Live Overview

Auto-refreshes every 8 seconds via `setInterval`.

Displays:
- 4 stat cards (Total Alerts, Critical, AI Triage Rate, Investigations)
- Bar chart: alerts by severity (Recharts)
- Pie chart: alerts by source (Recharts)
- Pipeline status: count per status stage
- AI verdict distribution: TP / FP / Suspicious / Benign

### 7.4 alerts/page.tsx — Alert List

- Auto-refreshes every 8 seconds
- Shows "+N new" indicator when new alerts arrive
- Severity filter buttons
- Table with: title, severity badge, source, MITRE ID, AI verdict, actions
- Click "Triage" to run AI triage
- Click "View" to see alert details

### 7.5 alerts/[id]/page.tsx — Alert Detail

Shows full alert information:
- Severity, source, MITRE mapping, OCSF class
- Network observables (IPs, hostname, username)
- AI Triage button → runs triage, shows verdict/confidence/reasoning
- AI Investigation button → runs 4-agent pipeline, shows:
  - Investigation summary and risk score
  - Full ledger with each agent's analysis
  - SHA-256 hash chain (hash of each step + link to previous)
  - Pseudonymization badges
  - Token count and processing time per step

### 7.6 evaluation/page.tsx — Metrics Dashboard

- Triage metrics: rate, reduction, confidence
- Verdict distribution with progress bars
- Investigation pipeline stats
- Ledger integrity verification
- Alert correlation groups with shared entities

### 7.7 lib/api.ts — API Client

Thin wrapper around `fetch()` for all API calls:
- `fetchDashboard()`, `fetchAlerts()`, `fetchAlert(id)`
- `triageAlert(id)`, `investigateAlert(id)`
- `fetchInvestigations()`, `updateAlertStatus(id, status)`

### 7.8 next.config.mjs — API Proxy

```javascript
rewrites: [{ source: "/api/:path*", destination: "http://localhost:8000/api/:path*" }]
```
This proxies all `/api/*` requests from the frontend (port 3000) to the backend (port 8000), avoiding CORS issues in the browser.

---

## 8. Data Flow — End to End

### Flow 1: Alert Ingestion
```
Network Monitor scans lsof → detects suspicious connection
    → creates Alert object with OCSF fields
    → saves to SQLite
    → auto-triages via Gemini
    → alert appears on Dashboard (next 8-second refresh)
```

### Flow 2: AI Triage
```
User clicks "Triage" on alert
    → POST /api/alerts/{id}/triage
    → Pseudonymizer masks IPs/hosts/users
    → Gemini receives sanitized prompt
    → Returns verdict JSON
    → Depseudonymize reasoning
    → Save verdict, confidence, priority to alert
    → Frontend updates
```

### Flow 3: Full Investigation
```
User clicks "Investigate"
    → POST /api/alerts/{id}/investigate
    → Create Investigation record
    → For each of 4 agents:
        1. Pseudonymize input
        2. Send to Gemini with agent-specific prompt
        3. Depseudonymize output
        4. Create LedgerEntry
        5. Compute SHA-256 hash (chain to previous)
    → Gemini summarizes all findings
    → Save investigation with risk score
    → Return full ledger to frontend
```

### Flow 4: Correlation
```
Every 60 seconds, correlation engine runs:
    → Fetch alerts from last 60 minutes
    → Extract entities (IP, host, user)
    → Group alerts sharing entities
    → Expand clusters transitively
    → Results available at /api/dashboard/correlations
```

---

## 9. Key Features Explained

### 9.1 OCSF (Open Cybersecurity Schema Framework)
Industry standard for normalizing security events. Our alerts include:
- `ocsf_class_uid`: Event type (2001=Security Finding, 4001=Network Activity)
- `ocsf_severity_id`: 1(Info) to 5(Critical)
- `ocsf_type_uid`: Full event type identifier

This means alerts from different sources (EDR, SIEM, Firewall) all follow the same schema.

### 9.2 MITRE ATT&CK Mapping
Every alert is tagged with the specific attack technique from the MITRE ATT&CK framework:
- **Tactic**: High-level goal (e.g., "Credential Access")
- **Technique**: Specific method (e.g., "Brute Force")
- **ID**: Reference number (e.g., "T1110")

### 9.3 SHA-256 Hash Chain
Like a mini blockchain for audit records:
```
Entry 1: hash = SHA256(content + "000...0")     ← genesis
Entry 2: hash = SHA256(content + Entry1.hash)    ← chains to 1
Entry 3: hash = SHA256(content + Entry2.hash)    ← chains to 2
Entry 4: hash = SHA256(content + Entry3.hash)    ← chains to 3
```
If anyone tampers with Entry 2, its hash changes, which breaks Entry 3's hash, which breaks Entry 4's hash → tamper detected.

### 9.4 Pseudonymization
```
Before LLM:  "Failed login from 10.0.1.15 on prod-web-01"
After mask:   "Failed login from [IP_001] on [HOST_001]"
LLM analyzes: "[IP_001] shows brute force pattern against [HOST_001]"
After unmask: "10.0.1.15 shows brute force pattern against prod-web-01"
```

---

## 10. API Endpoints (Complete Reference)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and status |
| GET | `/health` | Health check |
| GET | `/api/alerts` | List alerts (optional: ?severity=&status=) |
| GET | `/api/alerts/{id}` | Get alert by ID |
| POST | `/api/alerts/{id}/triage` | AI triage alert |
| POST | `/api/alerts/{id}/investigate` | Full AI investigation |
| PATCH | `/api/alerts/{id}/status?status=` | Update alert status |
| GET | `/api/dashboard` | Dashboard metrics |
| GET | `/api/dashboard/evaluation` | Evaluation harness |
| GET | `/api/dashboard/correlations` | Correlated alert groups |
| GET | `/api/investigations` | List investigations |
| GET | `/api/investigations/{id}` | Investigation + ledger |
| GET | `/api/investigations/ledger/all` | All ledger entries |
| GET | `/docs` | Swagger API documentation (auto-generated) |

---

## 11. How to Run

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm (install via: `npm install -g pnpm`)

### Terminal 1 — Backend
```bash
cd OUR_AiSOC/backend
pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd OUR_AiSOC/frontend
pnpm install
pnpm dev
```

### Open Browser
- http://localhost:3000 — Dashboard
- http://localhost:8000/docs — API Documentation

### Optional: Gemini API Key
```bash
# Edit .env file
GEMINI_API_KEY=your_key_from_aistudio.google.com
```

---

## 12. Synopsis Mapping

| Synopsis Objective | Implementation | File |
|-------------------|----------------|------|
| Obj #1: OCSF normalization + MITRE | `apply_ocsf()`, mitre fields | models.py |
| Obj #2: Alert correlation/fusion | Entity + temporal grouping | correlation.py |
| Obj #3: Multi-agent pipeline | 4 agents: triage→enrich→forensic→response | ai_engine.py |
| Obj #4: Investigator orchestrator | Sequential pipeline with context passing | ai_engine.py |
| Obj #5: Investigation Ledger (SHA-256) | Hash chain, immutable entries | models.py, ai_engine.py |
| Obj #6: Pseudonymization | Reversible IP/host/user masking | pseudonymizer.py |
| Obj #7: SOC Console | Next.js dashboard with live refresh | frontend/src/ |
| Obj #8: Agent tool ecosystem | Enrichment, MITRE lookup in agents | ai_engine.py |
| Obj #9: Evaluation harness | Triage rate, reduction, confidence | dashboard.py |
| Obj #10: Docker deployment | Simplified to pip + pnpm (BTech appropriate) | run.txt |
| Obj #12: Documentation | This guide + README | PROJECT_GUIDE.md |

---

*Document generated for Gen AI Capstone Project viva preparation.*
*AiSOC — Group 4, PCCOE Pune, 2026-2027*
