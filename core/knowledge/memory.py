"""Knowledge Engine persistente y verificable.

Inspirado en las capacidades de memoria central de Auto-LDS, pero
desacoplado de un dominio, proveedor de IA o framework de automatización.

Principios:
- El conocimiento vive dentro del repositorio.
- Nunca se ejecuta contenido almacenado como código.
- Las entradas nuevas son PROVISIONAL por defecto.
- VERIFICADO requiere una operación explícita.
- INVALIDADO y REEMPLAZADO conservan historial.
- Las consultas registran qué conocimiento se consultó, aplicó y descartó.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.common.enums import KnowledgeState, KnowledgeType
from core.common.exceptions import KnowledgeError


INDEX_FILENAME = "index.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _entries_dir(root: Path) -> Path:
    return root / "entries"


def _queries_dir(root: Path) -> Path:
    return root / "queries"


def _index_path(root: Path) -> Path:
    return root / INDEX_FILENAME


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise KnowledgeError(
            f"No se pudo leer JSON válido: {path}"
        ) from exc


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _load_index(root: Path) -> dict:
    return _read_json(
        _index_path(root),
        {
            "schema_version": "1.0",
            "entries": {},
            "updated_at": None,
        },
    )


def _save_index(root: Path, index: dict) -> None:
    index["updated_at"] = _now()
    _write_json(_index_path(root), index)


def _next_id(root: Path) -> str:
    index = _load_index(root)

    numbers = []

    for entry_id in index.get("entries", {}):
        if not entry_id.startswith("KNOW-"):
            continue

        suffix = entry_id[5:]

        if suffix.isdigit():
            numbers.append(int(suffix))

    number = max(numbers) + 1 if numbers else 1

    return f"KNOW-{number:04d}"


def initialize(root: Path) -> None:
    """Inicializar estructura de conocimiento si todavía no existe."""

    _entries_dir(root).mkdir(parents=True, exist_ok=True)
    _queries_dir(root).mkdir(parents=True, exist_ok=True)

    if not _index_path(root).exists():
        _save_index(
            root,
            {
                "schema_version": "1.0",
                "entries": {},
                "updated_at": None,
            },
        )


def add(
    root: Path,
    *,
    type_: KnowledgeType,
    description: str,
    source: str,
    requirement_origin: str,
    module: str | None = None,
    environment: str | None = None,
    version: str | None = None,
    evidence_refs: list[str] | None = None,
    state: KnowledgeState = KnowledgeState.PROVISIONAL,
    revalidation_conditions: str | None = None,
    replaces: str | None = None,
) -> dict:
    """Agregar conocimiento.

    Una entrada nueva queda PROVISIONAL salvo que el caller indique
    explícitamente otro estado.

    Si `replaces` se informa, la entrada anterior queda REEMPLAZADA y
    ambas entradas permanecen vinculadas.
    """

    initialize(root)

    if not description.strip():
        raise KnowledgeError("description no puede estar vacío")

    if not source.strip():
        raise KnowledgeError("source no puede estar vacío")

    if not requirement_origin.strip():
        raise KnowledgeError(
            "requirement_origin no puede estar vacío"
        )

    previous = None

    if replaces:
        previous = read(root, replaces)

        if previous is None:
            raise KnowledgeError(
                f"No existe la entrada a reemplazar: {replaces}"
            )

        if previous["state"] in {
            KnowledgeState.INVALIDADO.value,
            KnowledgeState.REEMPLAZADO.value,
        }:
            raise KnowledgeError(
                f"No se puede reemplazar una entrada "
                f"no vigente: {replaces}"
            )

    entry_id = _next_id(root)
    timestamp = _now()

    entry = {
        "schema_version": "1.0",
        "id": entry_id,
        "type": type_.value,
        "description": description,
        "module": module,
        "environment": environment,
        "version": version,
        "source": source,
        "requirement_origin": requirement_origin,
        "evidence_refs": list(evidence_refs or []),
        "state": state.value,
        "created_at": timestamp,
        "last_verified_at": (
            timestamp
            if state == KnowledgeState.VERIFICADO
            else None
        ),
        "revalidation_conditions": revalidation_conditions,
        "replaces": replaces,
        "replaced_by": None,
        "invalid_reason": None,
    }

    _write_json(
        _entries_dir(root) / f"{entry_id}.json",
        entry,
    )

    index = _load_index(root)

    index["entries"][entry_id] = {
        "type": entry["type"],
        "state": entry["state"],
        "module": module,
        "environment": environment,
        "version": version,
        "source": source,
        "summary": (
            description[:120]
            + ("..." if len(description) > 120 else "")
        ),
    }

    if previous is not None:
        previous["state"] = KnowledgeState.REEMPLAZADO.value
        previous["replaced_by"] = entry_id

        _write_json(
            _entries_dir(root) / f"{replaces}.json",
            previous,
        )

        index["entries"][replaces]["state"] = (
            KnowledgeState.REEMPLAZADO.value
        )

    _save_index(root, index)

    return entry


def read(root: Path, entry_id: str) -> dict | None:
    """Leer una entrada por ID."""

    return _read_json(
        _entries_dir(root) / f"{entry_id}.json",
        None,
    )


def search(
    root: Path,
    *,
    type_: KnowledgeType | None = None,
    state: KnowledgeState | None = None,
    module: str | None = None,
    environment: str | None = None,
    version: str | None = None,
    current_only: bool = True,
) -> list[dict]:
    """Buscar conocimiento.

    current_only=True excluye INVALIDADO y REEMPLAZADO.
    """

    initialize(root)

    index = _load_index(root)
    results = []

    for entry_id, metadata in sorted(
        index.get("entries", {}).items()
    ):
        if type_ is not None:
            if metadata.get("type") != type_.value:
                continue

        if state is not None:
            if metadata.get("state") != state.value:
                continue

        if module is not None:
            if metadata.get("module") != module:
                continue

        if environment is not None:
            if metadata.get("environment") != environment:
                continue

        if version is not None:
            if metadata.get("version") != version:
                continue

        if current_only and metadata.get("state") in {
            KnowledgeState.INVALIDADO.value,
            KnowledgeState.REEMPLAZADO.value,
        }:
            continue

        entry = read(root, entry_id)

        if entry is not None:
            results.append(entry)

    return results


def verify(root: Path, entry_id: str) -> dict:
    """Marcar explícitamente una entrada como VERIFICADO."""

    entry = read(root, entry_id)

    if entry is None:
        raise KnowledgeError(
            f"No existe la entrada: {entry_id}"
        )

    if entry["state"] in {
        KnowledgeState.INVALIDADO.value,
        KnowledgeState.REEMPLAZADO.value,
    }:
        raise KnowledgeError(
            f"No se puede verificar una entrada "
            f"no vigente: {entry_id}"
        )

    entry["state"] = KnowledgeState.VERIFICADO.value
    entry["last_verified_at"] = _now()

    _write_json(
        _entries_dir(root) / f"{entry_id}.json",
        entry,
    )

    index = _load_index(root)
    index["entries"][entry_id]["state"] = (
        KnowledgeState.VERIFICADO.value
    )

    _save_index(root, index)

    return entry


def invalidate(
    root: Path,
    entry_id: str,
    reason: str,
) -> dict:
    """Invalidar sin eliminar historial."""

    if not reason.strip():
        raise KnowledgeError(
            "La invalidación requiere un motivo"
        )

    entry = read(root, entry_id)

    if entry is None:
        raise KnowledgeError(
            f"No existe la entrada: {entry_id}"
        )

    entry["state"] = KnowledgeState.INVALIDADO.value
    entry["invalid_reason"] = reason

    _write_json(
        _entries_dir(root) / f"{entry_id}.json",
        entry,
    )

    index = _load_index(root)
    index["entries"][entry_id]["state"] = (
        KnowledgeState.INVALIDADO.value
    )

    _save_index(root, index)

    return entry


def register_query(
    root: Path,
    *,
    requirement: str,
    consulted: list[str],
    applied: list[str],
    discarded: dict[str, str],
) -> Path:
    """Registrar el uso de conocimiento para un requerimiento."""

    initialize(root)

    if not requirement.strip():
        raise KnowledgeError(
            "requirement no puede estar vacío"
        )

    consulted_set = set(consulted)

    unknown_applied = set(applied) - consulted_set

    if unknown_applied:
        raise KnowledgeError(
            "No se puede aplicar conocimiento que no fue "
            f"consultado: {sorted(unknown_applied)}"
        )

    unknown_discarded = set(discarded) - consulted_set

    if unknown_discarded:
        raise KnowledgeError(
            "No se puede descartar conocimiento que no fue "
            f"consultado: {sorted(unknown_discarded)}"
        )

    for entry_id in consulted:
        if read(root, entry_id) is None:
            raise KnowledgeError(
                f"Entrada consultada inexistente: {entry_id}"
            )

    record = {
        "schema_version": "1.0",
        "requirement": requirement,
        "timestamp": _now(),
        "consulted": list(consulted),
        "applied": list(applied),
        "discarded": dict(discarded),
    }

    path = _queries_dir(root) / f"{requirement}.json"

    _write_json(path, record)

    return path


def has_query(root: Path, requirement: str) -> bool:
    return (
        _queries_dir(root)
        / f"{requirement}.json"
    ).is_file()


def read_query(
    root: Path,
    requirement: str,
) -> dict | None:
    return _read_json(
        _queries_dir(root) / f"{requirement}.json",
        None,
    )
