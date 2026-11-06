"""Evidence Engine determinístico.

La evidencia no se considera válida porque un agente diga que existe.

El Core verifica:
- identidad run/case/attempt;
- archivos físicos;
- tipo de evidencia;
- tamaño;
- SHA-256;
- requisitos mínimos del perfil.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.common.exceptions import EvidenceError
from core.paths import (
    evidence_attempt_dir,
    evidence_manifest_path,
)


SCHEMA_VERSION = "1.0"

ALLOWED_TYPES = {
    "TRACE",
    "SCREENSHOT",
    "VIDEO",
    "LOG",
    "NETWORK",
    "REPORT",
    "OTHER",
}


@dataclass(frozen=True)
class EvidenceRequirement:
    required_types: tuple[str, ...] = ("TRACE",)
    require_any_of: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceItem:
    type: str
    path: str
    sha256: str
    size_bytes: int
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as exc:
        raise EvidenceError(
            f"Manifest inválido: {path}"
        ) from exc


def _write_json(
    path: Path,
    data: dict,
) -> Path:
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


def create_manifest(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> dict:
    if not run_id.strip():
        raise EvidenceError(
            "run_id no puede estar vacío"
        )

    if not case_id.strip():
        raise EvidenceError(
            "case_id no puede estar vacío"
        )

    if attempt < 1:
        raise EvidenceError(
            "attempt debe ser >= 1"
        )

    path = evidence_manifest_path(
        root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
    )

    if path.exists():
        raise EvidenceError(
            "Ya existe manifest para "
            f"{run_id}/{case_id}/{attempt}"
        )

    timestamp = _now()

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "case_id": case_id,
        "attempt": attempt,
        "items": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    _write_json(path, manifest)

    return manifest


def read_manifest(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> dict | None:
    return _read_json(
        evidence_manifest_path(
            root,
            run_id=run_id,
            case_id=case_id,
            attempt=attempt,
        )
    )


def _load_required(
    root: Path,
    run_id: str,
    case_id: str,
    attempt: int,
) -> dict:
    manifest = read_manifest(
        root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
    )

    if manifest is None:
        raise EvidenceError(
            "No existe manifest para "
            f"{run_id}/{case_id}/{attempt}"
        )

    return manifest


def register_file(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
    evidence_type: str,
    file_path: Path,
) -> dict:
    evidence_type = evidence_type.upper()

    if evidence_type not in ALLOWED_TYPES:
        raise EvidenceError(
            f"Tipo de evidencia inválido: "
            f"{evidence_type}"
        )

    if not file_path.is_file():
        raise EvidenceError(
            f"No existe evidencia física: "
            f"{file_path}"
        )

    manifest = _load_required(
        root,
        run_id,
        case_id,
        attempt,
    )

    try:
        relative = str(
            file_path.resolve().relative_to(
                root.resolve()
            )
        )
    except ValueError:
        raise EvidenceError(
            "La evidencia debe vivir dentro "
            "del evidence root."
        )

    item = EvidenceItem(
        type=evidence_type,
        path=relative,
        sha256=_sha256(file_path),
        size_bytes=file_path.stat().st_size,
        created_at=_now(),
    ).to_dict()

    existing = [
        current
        for current in manifest["items"]
        if current["path"] == relative
    ]

    if existing:
        if existing[0] != item:
            raise EvidenceError(
                "La evidencia ya fue registrada "
                "pero su contenido cambió."
            )

        return manifest

    manifest["items"].append(item)
    manifest["updated_at"] = _now()

    _write_json(
        evidence_manifest_path(
            root,
            run_id=run_id,
            case_id=case_id,
            attempt=attempt,
        ),
        manifest,
    )

    return manifest


def validate_manifest(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
    requirement: EvidenceRequirement | None = None,
) -> dict:
    requirement = (
        requirement
        if requirement is not None
        else EvidenceRequirement()
    )

    manifest = _load_required(
        root,
        run_id,
        case_id,
        attempt,
    )

    findings: list[str] = []
    valid_types: set[str] = set()

    if manifest.get("run_id") != run_id:
        findings.append("run_id_mismatch")

    if manifest.get("case_id") != case_id:
        findings.append("case_id_mismatch")

    if manifest.get("attempt") != attempt:
        findings.append("attempt_mismatch")

    for item in manifest.get("items", []):
        evidence_type = item.get("type")
        relative = item.get("path")

        if evidence_type not in ALLOWED_TYPES:
            findings.append(
                f"invalid_type={evidence_type}"
            )
            continue

        if not relative:
            findings.append(
                "evidence_path_missing"
            )
            continue

        path = root / relative

        if not path.is_file():
            findings.append(
                f"file_missing={relative}"
            )
            continue

        size = path.stat().st_size

        if size <= 0:
            findings.append(
                f"file_empty={relative}"
            )
            continue

        if size != item.get("size_bytes"):
            findings.append(
                f"size_mismatch={relative}"
            )
            continue

        digest = _sha256(path)

        if digest != item.get("sha256"):
            findings.append(
                f"sha256_mismatch={relative}"
            )
            continue

        valid_types.add(evidence_type)

    for required_type in requirement.required_types:
        if required_type not in valid_types:
            findings.append(
                f"required_type_missing="
                f"{required_type}"
            )

    if requirement.require_any_of:
        if not any(
            item in valid_types
            for item in requirement.require_any_of
        ):
            findings.append(
                "required_any_missing="
                + ",".join(
                    requirement.require_any_of
                )
            )

    return {
        "run_id": run_id,
        "case_id": case_id,
        "attempt": attempt,
        "complete": not findings,
        "valid_types": sorted(valid_types),
        "findings": findings,
        "manifest": str(
            evidence_manifest_path(
                root,
                run_id=run_id,
                case_id=case_id,
                attempt=attempt,
            )
        ),
    }
