# Fusion Transcript Oncology Agent

A Python and browser-based **demonstration of deterministic audit rules** for synthetic oncology-themed records. The repository includes a command-line interface, a FastAPI service, a standalone browser demo, and retained experimental/legacy modules.

**Scientific limitation:** This is **not** a fusion-transcript caller, breakpoint/frame validator, molecular pathology interpretation engine, ESCAT actionability scorer, drug matcher, or clinically validated decision-support system. The primary (>25) and secondary (>12) thresholds are arbitrary software demonstration settings, not clinical reference intervals. The status keywords and priority flag are likewise illustrative. Do not use outputs for clinical diagnosis, triage, therapy selection, or research conclusions about fusion biology.

## Features

- Three deterministic workers: primary-threshold check, priority/secondary-threshold check, and descriptor-keyword check.
- A supervisor combines alerts into an evaluation dossier.
- CLI supports single evaluations, CSV batches, a deterministic mock chat, and in-process audit verification.
- In-memory HMAC-SHA256 chained audit records, with signature and chain verification; **not** durable or independently timestamped audit storage.
- Optional authenticated FastAPI endpoints for local development.
- Static, responsive browser UI that executes comparable rules locally and downloads JSON. No Python runtime or API server is needed for the browser UI.

## Browser demonstration

The `web/index.html` file is a self-contained static application with `web/app.js`. Open it in a browser or serve the `web/` folder with a static file server. It does not submit data to a remote API, persist input, generate HMAC signatures, or process RNA-seq/NGS files. Do not enter identifiable patient information.

## Python CLI

Python 3.10+ is required.

```bash
python -m pip install -e ".[api,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fusion-transcript-oncology-agent audit --task-id TASK-001 --target SYNTH-001 --primary 28.5 --secondary 14.2 --status DISCORDANT
fusion-transcript-oncology-agent batch -i sample_task.csv -o results.csv
fusion-transcript-oncology-agent verify-audit
python -m pytest -q
```

The `sample_task.csv` file matches the primary supervisor CLI. The older `sample.csv` corresponds to the separate legacy packaged workflow (`fusion-transcript-oncology-engine` command) and uses different field names.

CSV values for `is_critical_flag` accept `true/false`, `1/0`, `yes/no`, and blank as false. The input CSV must contain `primary_metric`. Input and output paths must be relative to the current working directory, and output must differ from input.

## Local REST API

```bash
export API_ACCESS_TOKEN="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fusion-transcript-oncology-agent serve --host 127.0.0.1 --port 8000
curl -H "X-API-Key: $API_ACCESS_TOKEN" -H "Content-Type: application/json" \
  -d '{"task_id":"TASK-001","target_identifier":"SYNTH-001","primary_metric":10.0}' \
  http://127.0.0.1:8000/api/audit
```

`GET /health` does not require a token. Other endpoints (`/metrics`, `/api/audit`, `/api/chat`, `/api/audit/logs`) require the `X-API-Key` header. The API cannot serve real patient data safely without further controls such as formal authorization, encryption, retention policy, and privacy validation.

For local Docker deployment, set both `AUDIT_SECRET_KEY` and `API_ACCESS_TOKEN` in your shell before running `docker compose up --build`. Compose binds to `127.0.0.1:8000` by default.

## Privacy and security

The browser demo keeps entered data in page memory until reset or navigation; the JSON download is user-initiated. It uses no network API, analytics, cookies, external font services, or browser storage. The Python API stores dossiers and the audit chain in process memory only; they are lost when the process exits. The rule-based PHI check detects some common identifier patterns but **does not guarantee de-identification or HIPAA compliance**. Use synthetic data only.

## Implementation and testing

The primary supervisor is implemented in `agents/` and `cli.py`; `fusion_transcript_oncology_agent/` and `fusion_mind.py` contain distinct retained legacy examples. Changes to threshold rules should be tested for consistency between `agents/workers.py` and `web/app.js`. CI runs Python tests on 3.10–3.12 and browser-rule tests on Node.js.

All browser code uses standard HTML, CSS, and JavaScript, without a build tool or external dependencies. Recent evergreen desktop and mobile browsers are supported.

## License

MIT — see [LICENSE](LICENSE).
