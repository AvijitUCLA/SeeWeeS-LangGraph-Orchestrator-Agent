# SeeWeeS LangGraph Orchestrator Agent

A **multi-agent AI pipeline** built with [LangGraph](https://github.com/langchain-ai/langgraph) + [LangChain](https://github.com/langchain-ai/langchain) for the UCLA MSBA Industry Seminar.

The system automates operations and dispatch planning for **SeeWeeS Specialty Distribution** — reading business rules from a PDF, analyzing incoming shipment data, pulling live weather risk across an I-95 corridor, producing a compliance-checked dispatch plan, and emailing a leadership-ready HTML report.

---

## Architecture

```
pdf_context → csv_analysis → weather → planner → audit ─┐
                                                          ├─(PASS + risk < 2)──→ report → email → END
                                                          ├─(PASS + risk ≥ 2)──→ human_review → report → email → END
                                                          └─(FAIL)─────────────→ planner (retry loop)
```

### Agents

| Agent | Role |
|---|---|
| **ContextAgent** | RAG over the Dispatch Playbook PDF — extracts KPIs, SLAs, dispatch rules |
| **OpsDataAgent** | Analyzes incoming shipment CSV — computes KPIs, detects anomalies |
| **WeatherNode** | Fetches live weather (Open-Meteo) for each I-95 waypoint; scores corridor risk 0–3 |
| **PlannerAgent** | Combines context + ops insights + weather risk into a 24–48h dispatch plan |
| **AuditAgent** | Validates plan against business rules — loops back to Planner on failure |
| **Human Review** | Interrupts execution for manager approval when weather risk score ≥ 2 |
| **ReportAgent** | Generates a polished HTML report for leadership |
| **EmailNode** | Sends the report via SMTP (Gmail or Zoho) |

---

## Project Structure

```
.
├── data/
│   ├── SeeWeeS Specialty Dispatch Playbook.pdf   # Business rules + waypoint definitions (RAG source)
│   ├── About SeeWeeS Specialty distribution.pdf  # Company background
│   └── Incoming_shipment_03_06.csv               # Incoming shipment dataset
├── src/
│   ├── main.py          # Entry point — builds and runs the LangGraph pipeline
│   ├── graph.py         # LangGraph state machine: nodes + edges + conditional routing
│   ├── agents.py        # LLM agent wrappers (Gemini 2.5 Flash via Vertex AI)
│   ├── prompts.py       # ChatPromptTemplates for each agent
│   ├── tracing.py       # LangSmith tracing initializer
│   └── tools/
│       ├── pdf_tools.py     # PDF ingestion + ChromaDB RAG builder
│       ├── csv_tools.py     # CSV KPI computation + anomaly detection
│       ├── weather_tools.py # Open-Meteo API + risk scoring
│       └── email_tools.py   # SMTP email sender
├── chroma_db/           # Local vector store (auto-generated, not committed)
├── report.html          # Last generated output report (auto-generated)
├── requirements.txt
├── .env.example         # Environment variable template — copy to .env and fill in
└── README.md
```

---

## Environment Setup

### Prerequisites

- **Python 3.11** (recommended; 3.10+ required)
- A **Google Cloud** project with Vertex AI enabled and `gemini-2.5-flash` access
- Application Default Credentials configured: `gcloud auth application-default login`
- A **Gmail** or **Zoho** account with an app password for SMTP
- (Optional) A **LangSmith** account for tracing

### Step 1 — Clone the repository

```bash
git clone https://github.com/avijitUCLA/SeeWeeS-LangGraph-Orchestrator-Agent.git
cd SeeWeeS-LangGraph-Orchestrator-Agent
```

### Step 2 — Create and activate a virtual environment

**macOS / Linux:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

```bash
# macOS/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Open `.env` and fill in every value. See the table below:

| Variable | Description |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` or `smtp.zoho.com` |
| `SMTP_PORT` | `465` (SSL) |
| `SMTP_USER` | Your sender email address |
| `SMTP_PASSWORD` | Gmail/Zoho **app password** (not your login password) |
| `REPORT_EMAIL_TO` | Recipient email for the final report |
| `LANGCHAIN_TRACING_V2` | `true` to enable LangSmith tracing (optional) |
| `LANGCHAIN_API_KEY` | Your LangSmith API key (optional) |
| `LANGCHAIN_PROJECT` | LangSmith project name (optional) |
| `LANGCHAIN_ENDPOINT` | `https://api.smith.langchain.com` (optional) |
| `WEATHER_LAT` | Fallback latitude if waypoint parsing fails (default: `40.7282`) |
| `WEATHER_LON` | Fallback longitude if waypoint parsing fails (default: `-74.0776`) |
| `WEATHER_TZ` | Timezone string (default: `America/New_York`) |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

### Step 5 — Authenticate with Google Cloud (Vertex AI)

```bash
gcloud auth application-default login
```

Ensure your project has the **Vertex AI API** enabled and your account has access to `gemini-2.5-flash`.

---

## Running the Pipeline

```bash
# From the project root
python src/main.py
```

### What happens end-to-end:

1. **PDF RAG** — The Dispatch Playbook is chunked and stored in ChromaDB; business rules are retrieved
2. **CSV Analysis** — `Incoming_shipment_03_06.csv` is loaded; KPIs computed, anomalies flagged
3. **Weather** — Live forecast fetched for each I-95 waypoint (W1–W5) via Open-Meteo; corridor risk scored 0–3
4. **Planner** — Dispatch plan generated for the next 24–48h including weather buffer recommendations
5. **Audit** — Plan validated against business rules; loops until `PASS`
6. **Human Review** *(if weather risk ≥ 2)* — Execution pauses; you will be prompted in the terminal:
   ```
   Manager, please type 'Approve' to proceed or provide feedback:
   ```
7. **Report** — HTML report generated and saved to `report.html`
8. **Email** — Report emailed to `REPORT_EMAIL_TO` (skipped if not configured)

---

## Key Design Patterns

- **RAG (Retrieval-Augmented Generation)** — PDF business rules are embedded in ChromaDB and retrieved per query, keeping LLM prompts grounded
- **Audit-loop** — AuditAgent enforces compliance; PlannerAgent retries until the plan passes
- **Human-in-the-loop** — LangGraph's `interrupt_before` mechanism pauses the graph for manager approval on high-risk weather scenarios
- **Route-level weather scoring** — Weather is checked at each corridor waypoint; the worst score drives the risk level
- **LangSmith tracing** — Full agent traces visible in the LangSmith dashboard when configured

---

## Augmented Dataset

The `data/` directory contains:
- `SeeWeeS Specialty Dispatch Playbook.pdf` — Primary RAG source with KPI definitions, SLAs, dispatch constraints, and I-95 corridor waypoints
- `About SeeWeeS Specialty distribution.pdf` — Business background document
- `Incoming_shipment_03_06.csv` — Sample incoming shipment data (March 6) used for KPI analysis and anomaly detection

---

## License

For academic use — UCLA MSBA Industry Seminar demo project.