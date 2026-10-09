# AiSOC — AI-Driven Security Operations Center

> **Gen AI Capstone Project** | Group 4 | Pimpri Chinchwad College of Engineering (PCCOE), Pune
> Department of Computer Science & Engineering (AI & ML) | Academic Year 2026–2027

## Team

| Name | PRN | Role |
|------|-----|------|
| **Shubham Nemade** | 123B1B020 | Full-Stack Development, System Architecture |
| **Anushka Somawanshi** | 123B1B039 | AI Agent Pipeline, Investigation Ledger |
| **Atharva Karale** | 123B1B012 | Alert Engine, Event Processing, Correlation |

**Guide:** Prof. Santwana Ingole | **HOD:** Prof. Anuradha Thakare

## Overview

AiSOC is an AI-driven Security Operations Center that uses Google Gemini (Gen AI) to automate alert triage, multi-step investigation, and threat analysis. The system implements the complete SOC pipeline from event ingestion to AI-powered investigation with full auditability.

### Key Features

| Feature | Synopsis Objective | Implementation |
|---------|-------------------|----------------|
| **Multi-Agent Investigation Pipeline** | Obj #3, #4 | 4 agents: Triage → Enrichment → Forensic → Response |
| **Investigation Ledger (SHA-256)** | Obj #5 | Immutable audit trail with cryptographic hash chain |
| **Pseudonymization Module** | Obj #6 | Reversible masking of IPs/hostnames/users before LLM |
| **OCSF Normalization** | Obj #1 | Events normalized to Open Cybersecurity Schema Framework |
| **Alert Correlation Engine** | Obj #2 | Temporal & entity-based grouping of related alerts |
| **MITRE ATT&CK Mapping** | Obj #1 | All alerts mapped to ATT&CK tactics/techniques |
| **SOC Console** | Obj #7 | Real-time Next.js dashboard with live auto-refresh |
| **Evaluation Harness** | Obj #9 | Triage accuracy, alert reduction, ledger integrity metrics |
| **Real Network Monitoring** | Obj #1 | Live network traffic analysis on host device |
| **AI Triage (Gemini)** | Obj #3 | Automated classification with confidence scores |

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, Tailwind CSS, Recharts | SOC Console UI |
| Backend | FastAPI (Python) | REST API |
| Database | SQLite (async) | Zero-config storage |
| AI Engine | Google Gemini 1.5 Flash | Alert triage & investigation |
| Privacy | Custom pseudonymizer | Data masking before LLM calls |
| Integrity | SHA-256 hash chain | Tamper-evident investigation ledger |
| Standards | OCSF | Event normalization |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm (`npm install -g pnpm`)
- Google Gemini API key (free at https://aistudio.google.com/apikey)

### 1. Setup
```bash
cd OUR_AiSOC
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py                              # Seed 20 OCSF-normalized alerts
python -m uvicorn app.main:app --reload     # API at localhost:8000
```

### 3. Start Frontend
```bash
cd frontend
pnpm install
pnpm dev                                    # UI at localhost:3000
```

### 4. Open Browser
- **Dashboard:** http://localhost:3000
- **Alerts:** http://localhost:3000/alerts
- **Investigations:** http://localhost:3000/investigations
- **Evaluation:** http://localhost:3000/evaluation
- **API Docs:** http://localhost:8000/docs

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SOC Console (Next.js)                      │
│  Dashboard │ Alerts │ Investigations │ Evaluation Harness    │
└──────────────────────────┬───────────────────────────────────┘
                           │ REST API
┌──────────────────────────┴───────────────────────────────────┐
│                     FastAPI Backend                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Alert Ingestion Layer                       │ │
│  │  Network Monitor │ Alert Simulator │ OCSF Normalizer    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Correlation & Fusion Engine                    │ │
│  │  Entity matching │ Temporal grouping │ Alert clusters    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         Pseudonymization Module                          │ │
│  │  IP masking │ Hostname tokens │ User anonymization      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │        Multi-Agent Investigation Pipeline                │ │
│  │  TriageAgent → EnrichmentAgent → ForensicAgent →        │ │
│  │  ResponseAgent → Investigation Ledger (SHA-256)         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              SQLite Database                              │ │
│  │  alerts (OCSF) │ investigations │ ledger_entries (hash) │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Project Structure

```
OUR_AiSOC/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry + background services
│   │   ├── database.py          # SQLite async setup
│   │   ├── models.py            # ORM: Alert(OCSF), Investigation, LedgerEntry(SHA-256)
│   │   ├── routes/
│   │   │   ├── alerts.py        # CRUD + AI triage + investigation
│   │   │   ├── dashboard.py     # Metrics + evaluation + correlations
│   │   │   └── investigations.py
│   │   └── services/
│   │       ├── ai_engine.py        # Gemini AI pipeline + pseudonymization
│   │       ├── pseudonymizer.py    # Reversible data masking module
│   │       ├── correlation.py      # Entity-based alert correlation
│   │       ├── network_monitor.py  # Real network traffic monitor
│   │       └── simulator.py        # Synthetic alert generator
│   ├── seed.py
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── page.tsx             # Live Dashboard
│       ├── alerts/              # Alert list + detail (hash chain view)
│       ├── investigations/      # Investigation reports
│       └── evaluation/          # Evaluation harness metrics
├── .env.example
└── README.md
```

## Synopsis Compliance

| Synopsis Objective | Status |
|-------------------|--------|
| OCSF normalization + MITRE mapping | ✅ |
| Alert correlation/fusion engine | ✅ |
| Multi-agent LangGraph investigation | ✅ |
| Investigation Ledger with SHA-256 | ✅ |
| Pseudonymization module | ✅ |
| SOC Console with real-time streaming | ✅ |
| Evaluation harness | ✅ |
| Synthetic telemetry for demo | ✅ |
| Real network monitoring | ✅ (beyond scope) |

## License

MIT License — © 2026 Shubham Nemade, Anushka Somawanshi, Atharva Karale
PCCOE, Department of CSE (AI & ML)
