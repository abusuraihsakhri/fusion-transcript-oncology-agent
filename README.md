# Fusion Transcript Oncology Agent

> **Domain:** Medical Oncology & Cancer Staging Systems  
> **Reference Guidelines & Standards:** `AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Fusion Transcript Oncology Agent** is an advanced analytical and computational platform implementing Kinase Fusion (NTRK/RET/ALK/ROS1) & ESCAT Scale Matcher.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`BreakpointFrameValidatorAgent`**: Specialized Sub-Agent 1 for fusion-transcript-oncology-agent
- **`ESCATActionabilityScorerAgent`**: Specialized Sub-Agent 2 for fusion-transcript-oncology-agent
- **`TargetedInhibitorMatcherAgent`**: Specialized Sub-Agent 3 for fusion-transcript-oncology-agent

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
```

### Environment Setup

The audit trail requires a secure HMAC-SHA256 key. Generate one and set it:
```bash
# Generate a secure key
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### 1. Run a Single Audit
```bash
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
```

### 2. Batch Process a CSV File
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Query the Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### CLI Commands

| Command | Description |
|:--------|:------------|
| `audit` | Run a single task evaluation across specialized workers |
| `batch` | Batch process CSV records (input/output restricted to CWD) |
| `chat` | Query the air-gapped supervisory assistant |
| `verify-audit` | Verify HMAC-SHA256 audit trail cryptographic integrity |
| `serve` | Launch FastAPI REST API server |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier (max 128 chars) | Required |
| `target_identifier` | Specimen or target key (max 128 chars) | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary kinetic/confidence score | Optional (default 0.0) |
| `status_descriptor` | Status code or phenotype (max 64 chars) | Optional (default "NOMINAL") |
| `is_critical_flag` | Emergency escalation trigger | Optional (default false) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite (requires `AUDIT_SECRET_KEY`):

```bash
export AUDIT_SECRET_KEY="test-key-for-development-only"
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 100
```

---

## 🐳 Container Deployment

```bash
docker build -t fusion-transcript-oncology-agent .
docker run -p 8000:8000 fusion-transcript-oncology-agent
```
