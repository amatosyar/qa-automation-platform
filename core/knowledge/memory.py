"""Memoria verificable, agnostica de proveedor y almacenada en el repositorio."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

TYPES = {"REGLA_DOCUMENTADA","COMPORTAMIENTO_OBSERVADO","SOLUCION_TECNICA_COMPROBADA","DATO_DE_PRUEBA","INTERVENCION_MANUAL","DUDA_PENDIENTE"}
STATES = {"PROVISIONAL","VERIFICADO","INVALIDADO","REEMPLAZADO"}

def _load(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return default

def search(root: Path, *, type_: str|None=None, state: str|None=None, current_only: bool=True):
    entries = root / "entries"
    out=[]
    for p in sorted(entries.glob("KNOW-*.json")) if entries.exists() else []:
        e=_load(p,{})
        if type_ and e.get("type") != type_: continue
        if state and e.get("state") != state: continue
        if current_only and e.get("state") in {"INVALIDADO","REEMPLAZADO"}: continue
        out.append(e)
    return out

def add(root: Path, *, type_: str, description: str, source: str, evidence_refs=None, state="PROVISIONAL"):
    if type_ not in TYPES or state not in STATES: raise ValueError("tipo/estado invalido")
    entries=root/"entries"; entries.mkdir(parents=True, exist_ok=True)
    nums=[int(p.stem.split("-")[-1]) for p in entries.glob("KNOW-*.json") if p.stem.split("-")[-1].isdigit()]
    id_=f"KNOW-{(max(nums)+1 if nums else 1):04d}"
    obj={"id":id_,"type":type_,"description":description,"source":source,"evidence_refs":evidence_refs or [],"state":state,"created_at":datetime.now().isoformat()}
    (entries/f"{id_}.json").write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
    return obj
