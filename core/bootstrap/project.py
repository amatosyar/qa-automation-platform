"""Bootstrap determinístico de proyectos consumidores."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from core.artifacts import normalize_artifacts
from core.common.exceptions import QAPlatformError
from core.knowledge import initialize as initialize_knowledge


class BootstrapError(QAPlatformError):
    """Error creando un proyecto consumidor."""


REQUIRED_DIRECTORIES = (
    "documents/original",
    "documents/normalized",
    "tests",
    "pages",
    "components",
    "fixtures",
    "data",
    "utils",
    "knowledge",
    "traceability/cases",
    "evidence",
    "results",
    "reviews",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_source(path: Path, suffix: str, label: str) -> None:
    if not path.is_file():
        raise BootstrapError(
            f"{label} no existe: {path}"
        )

    if path.suffix.lower() != suffix:
        raise BootstrapError(
            f"{label} debe ser {suffix}: {path}"
        )


def _copy_source(
    source: Path,
    destination: Path,
) -> Path:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        source,
        destination,
    )

    return destination


def bootstrap_project(
    *,
    project_root: Path,
    matrix: Path,
    ef: Path,
    et: Path,
    force: bool = False,
) -> dict:
    """Crear proyecto consumidor.

    No modifica los artefactos originales.

    Si el proyecto ya fue inicializado, requiere force=True.
    """

    _validate_source(
        matrix,
        ".xlsx",
        "Matriz",
    )
    _validate_source(
        ef,
        ".docx",
        "EF",
    )
    _validate_source(
        et,
        ".docx",
        "ET",
    )

    marker = (
        project_root
        / ".qa-platform"
        / "bootstrap.json"
    )

    if marker.exists() and not force:
        raise BootstrapError(
            f"Proyecto ya inicializado: {project_root}"
        )

    project_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    for directory in REQUIRED_DIRECTORIES:
        (
            project_root
            / directory
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    originals = (
        project_root
        / "documents"
        / "original"
    )

    matrix_copy = _copy_source(
        matrix,
        originals / "matriz.xlsx",
    )

    ef_copy = _copy_source(
        ef,
        originals / "EF.docx",
    )

    et_copy = _copy_source(
        et,
        originals / "ET.docx",
    )

    normalized_dir = (
        project_root
        / "documents"
        / "normalized"
    )

    normalized = normalize_artifacts(
        matrix=matrix_copy,
        ef=ef_copy,
        et=et_copy,
        output_dir=normalized_dir,
    )

    initialize_knowledge(
        project_root / "knowledge"
    )

    marker.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "schema_version": "1.0",
        "created_at": _now(),
        "project_root": str(
            project_root.resolve()
        ),
        "sources": {
            "matrix": (
                "documents/original/matriz.xlsx"
            ),
            "ef": (
                "documents/original/EF.docx"
            ),
            "et": (
                "documents/original/ET.docx"
            ),
        },
        "normalized": {
            key: str(
                value.relative_to(
                    project_root
                )
            )
            for key, value
            in normalized.items()
        },
    }

    marker.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return metadata
