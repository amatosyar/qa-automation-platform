"""Traceability Engine.

Mantiene la relación verificable:

Matriz
-> EF / ET
-> Knowledge
-> Implementation
-> Execution
-> Evidence
-> Review

No duplica los artefactos fuente. Almacena referencias.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.common.exceptions import TraceabilityError


SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cases_dir(root: Path) -> Path:
    return root / "cases"


def _case_path(root: Path, case_id: str) -> Path:
    return _cases_dir(root) / f"{case_id}.json"


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as exc:
        raise TraceabilityError(
            f"No se pudo leer trazabilidad: {path}"
        ) from exc


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return path


def create_case(
    root: Path,
    *,
    case_id: str,
    matrix_ref: str,
) -> dict:
    """Crear trazabilidad inicial para un caso de la Matriz."""

    if not case_id.strip():
        raise TraceabilityError(
            "case_id no puede estar vacío"
        )

    if not matrix_ref.strip():
        raise TraceabilityError(
            "matrix_ref no puede estar vacío"
        )

    path = _case_path(root, case_id)

    if path.exists():
        raise TraceabilityError(
            f"Ya existe trazabilidad para: {case_id}"
        )

    timestamp = _now()

    record = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "matrix_ref": matrix_ref,
        "ef_refs": [],
        "et_refs": [],
        "knowledge_refs": [],
        "implementation_refs": [],
        "execution_refs": [],
        "evidence_refs": [],
        "review_refs": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    _write_json(path, record)

    return record


def read_case(
    root: Path,
    case_id: str,
) -> dict | None:
    return _read_json(
        _case_path(root, case_id)
    )


def _load_required(
    root: Path,
    case_id: str,
) -> dict:
    record = read_case(root, case_id)

    if record is None:
        raise TraceabilityError(
            f"No existe trazabilidad para: {case_id}"
        )

    return record


def _append_unique(
    root: Path,
    case_id: str,
    field: str,
    reference: str,
) -> dict:
    if not reference.strip():
        raise TraceabilityError(
            f"{field}: referencia vacía"
        )

    record = _load_required(
        root,
        case_id,
    )

    values = record[field]

    if reference not in values:
        values.append(reference)

    record["updated_at"] = _now()

    _write_json(
        _case_path(root, case_id),
        record,
    )

    return record


def add_ef_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "ef_refs",
        reference,
    )


def add_et_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "et_refs",
        reference,
    )


def add_knowledge_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "knowledge_refs",
        reference,
    )


def add_implementation_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "implementation_refs",
        reference,
    )


def add_execution_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "execution_refs",
        reference,
    )


def add_evidence_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "evidence_refs",
        reference,
    )


def add_review_ref(
    root: Path,
    case_id: str,
    reference: str,
) -> dict:
    return _append_unique(
        root,
        case_id,
        "review_refs",
        reference,
    )


def completeness(
    root: Path,
    case_id: str,
    *,
    require_ef: bool = True,
    require_et: bool = True,
    require_knowledge: bool = False,
) -> dict[str, Any]:
    """Evaluar completitud determinística.

    Knowledge no es obligatorio por defecto porque un caso puede no
    necesitar conocimiento histórico adicional.
    """

    record = _load_required(
        root,
        case_id,
    )

    checks = {
        "matrix": bool(
            record.get("matrix_ref")
        ),
        "ef": (
            bool(record["ef_refs"])
            if require_ef
            else True
        ),
        "et": (
            bool(record["et_refs"])
            if require_et
            else True
        ),
        "knowledge": (
            bool(record["knowledge_refs"])
            if require_knowledge
            else True
        ),
        "implementation": bool(
            record["implementation_refs"]
        ),
        "execution": bool(
            record["execution_refs"]
        ),
        "evidence": bool(
            record["evidence_refs"]
        ),
        "review": bool(
            record["review_refs"]
        ),
    }

    missing = [
        name
        for name, complete in checks.items()
        if not complete
    ]

    return {
        "case_id": case_id,
        "complete": not missing,
        "checks": checks,
        "missing": missing,
    }


def validate_reference_shapes(
    root: Path,
    case_id: str,
) -> dict:
    """Validaciones mínimas de forma.

    No afirma que el archivo físico exista todavía.
    Esa validación pertenece al resolver de referencias.
    """

    record = _load_required(
        root,
        case_id,
    )

    findings = []

    matrix_ref = record["matrix_ref"]

    if "#" not in matrix_ref:
        findings.append(
            {
                "field": "matrix_ref",
                "reference": matrix_ref,
                "reason": (
                    "La referencia no contiene "
                    "locator de procedencia."
                ),
            }
        )

    for field in (
        "ef_refs",
        "et_refs",
    ):
        for reference in record[field]:
            if "#" not in reference:
                findings.append(
                    {
                        "field": field,
                        "reference": reference,
                        "reason": (
                            "La referencia documental "
                            "no contiene locator."
                        ),
                    }
                )

    return {
        "case_id": case_id,
        "valid": not findings,
        "findings": findings,
    }
