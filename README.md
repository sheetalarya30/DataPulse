# DataPulse — AI-Powered Data Pipeline Diagnosis & Recovery Platform

> **Detect. Diagnose. Recover.**  
> An intelligent data pipeline monitoring, forensic root-cause diagnosis, and automated safe recovery platform built for modern data engineering.

---

## 1. System Architecture

DataPulse provides end-to-end observability and recovery for mission-critical data pipelines. Traditional schedulers often report a pipeline run as "successful" even when rows are dropped, keys are duplicated, or schemas silently drift. DataPulse reconciles actual record sets, runs granular data-quality guardrails, diagnoses root causes from factual execution logs, and enables safe, idempotent recovery without writing duplicate rows.

```
                                      +---------------------------------------------+
                                      |              DataPulse React SPA            |
                                      | (Vite + TypeScript + Tailwind + Recharts)   |
                                      +----------------------+----------------------+
                                                             | REST API (HTTP / JSON)
                                                             v
+-------------------------------------------------------------------------------------------------------------------+
|                                                 FastAPI Backend                                                   |
|                                                                                                                   |
|  +--------------------+  +----------------------+  +---------------------+  +----------------------------------+  |
|  |  Pipeline Runner   |  |   Data Quality Engine|  |   Diagnosis Engine  |  |         Recovery Engine          |  |
|  | - Extract (CSV/DB) |  | - Completeness Check |  | - Discrepancy Rule  |  | - Pre-flight safety check        |  |
|  | - Transform (Pandas|  | - Duplicate Check    |  | - Schema Anomaly    |  | - Idempotent Upsert / Merge      |  |
|  | - Load (Staging)   |  | - Reconciliation     |  | - Error Log Parsing |  | - Target Post-load validation   |  |
|  | - Metrics Logging  |  | - Format Validation  |  | - AI-Assisted (LLM) |  | - History & Audit preservation   |  |
|  |                    |  | - Schema Drift Check |  |   + Fallback Engine |  |                                  |  |
|  +---------+----------+  +----------+-----------+  +----------+----------+  +----------------+-----------------+  |
|            |                        |                         |                              |                    |
|            +------------------------+-------------------------+------------------------------+                    |
|                                                             |                                                     |
|                                              SQLAlchemy ORM Repositories                                          |
+-------------------------------------------------------------+-----------------------------------------------------+
                                                              |
                                                              v
                                  +-------------------------------------------------------+
                                  |                 PostgreSQL / Database                 |
                                  | - pipelines               - pipeline_runs             |
                                  | - execution_logs          - quality_check_results     |
                                  | - incidents               - recovery_attempts         |
                                  | - raw_orders (source)     - analytics_orders (target) |
                                  +-------------------------------------------------------+
```

---

## 2. Key Pages & Features

### A. Overview Dashboard (`/`)
- **Real-time Telemetry Metrics**: Total Pipeline Runs, Success Rate (%), Average Duration (seconds/ms), and Unresolved Incidents calculated directly from active database records.
- **Historical Failure Trends Chart**: Interactive Recharts area chart tracking daily throughput and failure spikes.
- **Quality Compliance Gauge**: Overall pass percentage across all validation assertions.
- **Active Incidents & Recent Pipeline Executions**: Instant insight into recent pipeline batches with scenario tags and direct drill-downs.

### B. Pipelines (`/pipelines`)
- Registered pipelines catalogue (*E-Commerce Orders Ingestion*, *Warehouse Inventory Sync*, *Clickstream Event Processor*).
- Live metrics: Source definition, Target warehouse, Cadence, Lifetime Success Ratio, and Total Runs.
- **"Execute Demo Scenario"**: Interactive modal allowing users to trigger any of the 7 deterministic test scenarios.

### C. Pipeline Details (`/pipelines/{id}`)
- Historical execution run selector with status pills (`success`, `failed`).
- **Chronological Execution Logs**: Stage-by-stage log streams (`EXTRACT`, `VALIDATE`, `TRANSFORM`, `LOAD`, `QUALITY_CHECK`) with severity filtering (`INFO`, `WARNING`, `ERROR`).
- **Quality Checks Tab**: Pass/fail status, evaluated rows, failed records count, and JSON details.

### D. Incident Investigation (`/incidents`)
- Real-time incident triage filtered by status (`UNRESOLVED`, `RESOLVED`).
- Error category classification: `RECORD_LOSS`, `DUPLICATE_KEYS`, `NULL_VIOLATION`, `FORMAT_ERROR`, `SCHEMA_MISMATCH`, `SYSTEM_FAILURE`.
- **Factual Root-Cause Summary**: Supported by confidence scores (92% - 99%).
- **Forensic Evidence Inspector**: Interactive JSON viewer displaying exact missing order IDs, duplicate keys, or column drift.
- **Recommended Recovery Steps**: Prescriptive remediation strategies.

### E. Data Quality Guardrails (`/quality`)
- 6 automated validation check suites:
  1. **Row Count Reconciliation (`RECONCILIATION`)**: Catches source vs target deficits.
  2. **Primary Key Uniqueness (`UNIQUENESS`)**: Prevents duplicate key collisions.
  3. **Mandatory Field Completeness (`COMPLETENESS`)**: Flags nulls in critical columns.
  4. **Schema Drift Conformance (`SCHEMA`)**: Detects missing or renamed columns.
  5. **Syntax & Boundary Validity (`FORMAT`)**: Asserts timestamp ISO standards, email regex, and non-negative amounts.
  6. **Volume Anomaly Threshold (`VOLUME`)**: Monitors batch throughput anomalies.
- **Recent Failures Inspector Modal**: Granular inspection of failed assertions and underlying records.

### F. Recovery Center (`/recovery`)
- Detects eligible failed runs and incidents requiring remediation.
- **Pre-Flight Safety Verification**: Asserts duplicate prevention guarantees and audit log preservation before retrying.
- **One-Click Safe Recovery**: Confirmation modal explaining planned action.
- **Idempotent Merge Execution**: Upserts cleansed entities into the target database without creating duplicate keys.
- **Audit Preservation**: The original failed run and its forensic logs remain permanently preserved; a new recovery run is linked as child and the incident is marked `RESOLVED`.

---

## 3. Seven Deterministic Test Scenarios

| Scenario | Injected Condition | Expected Quality Outcome | Incident Category |
|---|---|---|---|
| **1. Success** | 50 clean e-commerce records | All 6 check suites PASS (100% compliance) | None |
| **2. Missing Records** | Worker partition dropout dropping 10 rows | Reconciliation check FAILS (-10 deficit) | `RECORD_LOSS` |
| **3. Duplicate Orders** | 5 duplicate `order_id`s in batch | Uniqueness check FAILS (sample IDs isolated) | `DUPLICATE_KEYS` |
| **4. Null Values** | Missing `customer_email` & `amount` | Completeness check FAILS (null fields flagged) | `NULL_VIOLATION` |
| **5. Invalid Formats** | Corrupted dates & negative amounts | Format check FAILS (boundary errors isolated) | `FORMAT_ERROR` |
| **6. Schema Mismatch** | Column `order_id` renamed to `order_tracking_num` | Pre-load validation ABORTS | `SCHEMA_MISMATCH` |
| **7. Pipeline Failure** | Simulated database socket timeout during LOAD | Pipeline throws fatal exception; state saved | `SYSTEM_FAILURE` |

---

## 4. Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts, React Router v7, Lucide React.
- **Backend**: Python 3.14 / 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0.
- **Database**: PostgreSQL 18 (with automatic SQLite fallback for zero-dependency instant local launch).
- **Data Processing**: Python, Pandas, structured logging.
- **AI Diagnostics**: Configurable (`openai`, `gemini`, `rule_based`) with reliable, hallucination-free rule engine fallback.

---

## 5. Getting Started (Windows PowerShell)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (Optional; SQLite works automatically out of the box)

### Step 1: Clone and Activate Virtual Environment
```powershell
cd C:\DataPulse
.venv\Scripts\Activate.ps1
```

### Step 2: Install Backend Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
By default, `DATABASE_URL=sqlite:///./datapulse.db` is configured with `ALLOW_SQLITE_FALLBACK=true`.  
To use your local PostgreSQL 18 service, set:
```ini
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/datapulse
```

### Step 4: Seed Database
```powershell
$env:PYTHONPATH="backend"
python backend\scripts\seed_data.py
```

### Step 5: Run Automated Tests
```powershell
python -m pytest backend\tests -v
```
*Expected: 21 passed tests covering database models, all 7 ETL scenarios, API routes, metrics calculations, and safe recovery idempotency.*

### Step 6: Start Backend Server
In Terminal 1:
```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 7: Start Frontend Server
In Terminal 2:
```powershell
cd C:\DataPulse\frontend
npm run dev
```
Open your browser at: **[http://localhost:5173/](http://localhost:5173/)**
