"""Observabilidade e trilha de auditoria — Sprint 4 / Genera AI.
Privacy by design: conteúdo sensível só é persistido quando
GOVERNANCE_LOG_CONTENT=true (usar apenas com dados simulados/autorizados).
"""
from __future__ import annotations
import hashlib, json, logging, os, threading, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "sprint4" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = LOG_DIR / "audit.jsonl"
ALERT_FILE = LOG_DIR / "alerts.jsonl"
_CONTENT = os.getenv("GOVERNANCE_LOG_CONTENT", "false").lower() == "true"
_LOCK = threading.Lock()
_METRICS = {"executions":0,"success":0,"failures":0,"blocked":0,"total_latency_ms":0.0,"last_error":None,"last_execution":None}

def utc_now(): return datetime.now(timezone.utc).isoformat()
def pseudonymize(value: str) -> str:
    return hashlib.sha256((value or "anonymous").encode()).hexdigest()[:16]
def digest(value: str) -> str:
    return hashlib.sha256((value or "").encode()).hexdigest()
def _safe_content(value: str) -> str | None:
    return value if _CONTENT else None

def _append(path: Path, event: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str)+"\n")

def audit_event(*, event_type:str, session_id:str="", request_id:str="", status:str="info", duration_ms:float|None=None, question:str="", response:str="", sources:list|None=None, details:dict|None=None):
    sources=sources or []
    source_meta=[]
    for i,s in enumerate(sources):
        text = s.get("conteudo", "") if isinstance(s,dict) else str(s)
        source_meta.append({"position":i+1,"content_sha256":digest(text),"content":_safe_content(text)})
    event={"timestamp_utc":utc_now(),"event_id":str(uuid.uuid4()),"event_type":event_type,"request_id":request_id,"session_pseudonym":pseudonymize(session_id),"status":status,"duration_ms":round(duration_ms,2) if duration_ms is not None else None,"question_sha256":digest(question) if question else None,"response_sha256":digest(response) if response else None,"question":_safe_content(question),"response":_safe_content(response),"sources":source_meta,"details":details or {}}
    _append(AUDIT_FILE,event)
    return event

def record_execution(status:str, duration_ms:float, error:str|None=None):
    with _LOCK:
        _METRICS["executions"]+=1; _METRICS["total_latency_ms"]+=duration_ms; _METRICS["last_execution"]=utc_now()
        if status=="respondido": _METRICS["success"]+=1
        elif status=="bloqueado": _METRICS["blocked"]+=1
        else: _METRICS["failures"]+=1
        if error: _METRICS["last_error"]={"timestamp_utc":utc_now(),"type":error[:120]}

def metrics_snapshot():
    with _LOCK:
        m=dict(_METRICS)
    n=m["executions"]
    m["success_rate_pct"]=round(100*m["success"]/n,2) if n else 0.0
    m["average_latency_ms"]=round(m.pop("total_latency_ms")/n,2) if n else 0.0
    return m

def alert(code:str, severity:str, message:str, request_id:str="", details:dict|None=None):
    event={"timestamp_utc":utc_now(),"alert_id":str(uuid.uuid4()),"code":code,"severity":severity,"message":message,"request_id":request_id,"details":details or {}}
    _append(ALERT_FILE,event)
    logging.getLogger("genera.governance").warning("ALERT %s | %s | request_id=%s",code,message,request_id)
    return event

class Trace:
    def __init__(self, session_id:str): self.session_id=session_id; self.request_id=str(uuid.uuid4()); self.start=time.perf_counter()
    def elapsed_ms(self): return (time.perf_counter()-self.start)*1000
