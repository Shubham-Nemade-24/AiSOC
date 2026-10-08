# AiSOC — AI-Driven Security Operations Center

> **Gen AI Capstone Project** | Group 4 | Pimpri Chinchwad College of Engineering (PCCOE), Pune
> Department of Computer Science & Engineering (AI & ML) | Academic Year 2026–2027

## Team

| Name | PRN | Role |
|------|-----|------|
| **Shubham Nemade** | 123B1B020 | Full-Stack Development, System Architecture |
| **Anushka Somawanshi** | 123B1B039 | AI Agent Pipeline, Investigation Ledger |
| **Atharva Karale** | 123B1B012 | Alert Engine, Event Processing |

**Guide:** Prof. Santwana Ingole | **HOD:** Prof. Anuradha Thakare

## Overview

AiSOC is an AI-driven Security Operations Center that uses Google Gemini (Gen AI) to automate alert triage, multi-step investigation, and threat analysis. The system features a multi-agent investigation pipeline where specialized AI agents collaborate to analyze security alerts.

### Key Features

- **AI-Powered Alert Triage** — Automated classification using Gemini LLM
- **Multi-Agent Investigation Pipeline** — 4 specialized agents (Triage, Enrichment, Forensic, Response)
- **Investigation Ledger** — Immutable audit trail of every AI decision
- **MITRE ATT&CK Mapping** — Alerts mapped to real attack techniques
- **SOC Dashboard** — Real-time metrics and visualizations
- **20 Realistic Alert Types** — Pre-seeded security incidents

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, Tailwind CSS, Recharts | SOC Console UI |
| Backend | FastAPI (Python) | REST API |
| Database | SQLite | Zero-config storage |
| AI Engine | Google Gemini 1.5 Flash | Alert triage & investigation |
| Charts | Recharts | Dashboard visualizations |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm (`npm install -g pnpm`)
- Google Gemini API key (free at https://aistudio.google.com/apikey)

### 1. Clone & Setup
```bash
cd OUR_AiSOC

# Create .env with your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py                              # Seed 20 alerts
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
- **API Docs:** http://localhost:8000/docs

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    SOC Console (Next.js)                  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │ Dashboard │  │  Alerts  │  │   Investigation View   │ │
│  └──────────┘  └──────────┘  └────────────────────────┘ │
└───────────────────────┬──────────────────────────────────┘
                        │ REST API
┌───────────────────────┴──────────────────────────────────┐
│                   FastAPI Backend                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Alert CRUD │  │ AI Triage    │  │  Investigation   │ │
│  │            │  │ (Gemini LLM) │  │  Pipeline        │ │
│  └────────────┘  └──────────────┘  └──────────────────┘ │
│                           │                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │        Multi-Agent Investigation Pipeline            │ │
│  │  TriageAgent → EnrichmentAgent → ForensicAgent →    │ │
│  │  ResponseAgent → Investigation Ledger               │ │
│  └─────────────────────────────────────────────────────┘ │
│                           │                              │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              SQLite Database                         │ │
│  │  alerts │ investigations │ ledger_entries            │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Project Structure

```
OUR_AiSOC/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── database.py          # SQLite async setup
│   │   ├── models.py            # ORM models (Alert, Investigation, Ledger)
│   │   ├── routes/
│   │   │   ├── alerts.py        # Alert CRUD + AI triage
│   │   │   ├── dashboard.py     # Aggregate metrics
│   │   │   └── investigations.py # Investigation management
│   │   └── services/
│   │       └── ai_engine.py     # Gemini AI triage + investigation pipeline
│   ├── seed.py                  # Seed 20 realistic alerts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Dashboard
│   │   │   ├── alerts/          # Alert list + detail
│   │   │   └── investigations/  # Investigation reports
│   │   ├── components/
│   │   │   └── Sidebar.tsx      # Navigation sidebar
│   │   └── lib/
│   │       └── api.ts           # API client
│   └── package.json
├── .env.example
└── README.md
```

## License

MIT License — © 2026 Shubham Nemade, Anushka Somawanshi, Atharva Karale
PCCOE, Department of CSE (AI & ML)
