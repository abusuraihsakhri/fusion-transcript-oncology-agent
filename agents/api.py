"""Local FastAPI interface for the demonstration audit engine.

Set API_ACCESS_TOKEN before accepting requests. Do not submit patient data.
"""
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Fusion Transcript Oncology Agent API",
    description="Deterministic demonstration; not a validated clinical decision system.",
    version="3.0.1",
)


def require_api_token(x_api_key: str | None = Header(default=None)) -> None:
    configured = os.environ.get("API_ACCESS_TOKEN", "")
    if not configured:
        raise HTTPException(status_code=503, detail="API_ACCESS_TOKEN is not configured")
    if not x_api_key or not secrets.compare_digest(x_api_key, configured):
        raise HTTPException(status_code=401, detail="Invalid API access token")


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "fusion-transcript-oncology-agent",
            "mode": "demonstration", "version": "3.0.1"}


@app.get("/metrics", dependencies=[Depends(require_api_token)])
def metrics():
    return {"dossiers_processed_total": len(supervisor.dossier_registry),
            "audit_blocks_total": len(AuditLogger.get_trail())}


@app.post("/api/audit", dependencies=[Depends(require_api_token)])
def api_audit(payload: SystemTaskPayload):
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier")


@app.post("/api/chat", dependencies=[Depends(require_api_token)])
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a disallowed identifier")


@app.get("/api/audit/logs", dependencies=[Depends(require_api_token)])
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(),
            "verified": AuditLogger.verify_integrity()}
