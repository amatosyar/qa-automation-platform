"""Extracción estructural de EF/ET DOCX.

Preserva orden de párrafos y tablas.
No decide por sí mismo qué texto constituye un requisito.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import BadZipFile

from core.artifacts.io import sha256_file
from core.artifacts.models.artifact import (
    ArtifactType,
    NormalizedArtifact,
)
from core.common.exceptions import ArtifactError


def _load_docx():
    try:
        import docx
    except ImportError as exc:
        raise ArtifactError(
            "Se requiere python-docx para procesar archivos DOCX."
        ) from exc

    return docx


def extract_docx(
    path: Path,
    artifact_type: ArtifactType,
) -> NormalizedArtifact:
    if artifact_type not in {
        ArtifactType.EF,
        ArtifactType.ET,
    }:
        raise ArtifactError(
            "extract_docx solo acepta EF o ET."
        )

    if path.suffix.lower() != ".docx":
        raise ArtifactError(
            f"El artefacto debe ser .docx: {path}"
        )

    docx = _load_docx()

    try:
        document = docx.Document(path)
    except (OSError, BadZipFile, ValueError) as exc:
        raise ArtifactError(
            f"No se pudo abrir DOCX: {path}"
        ) from exc

    paragraphs = []

    for index, paragraph in enumerate(
        document.paragraphs,
        start=1,
    ):
        text = paragraph.text.strip()

        if not text:
            continue

        paragraphs.append(
            {
                "index": index,
                "source_ref": {
                    "file": path.name,
                    "locator": (
                        f"{path.name}#paragraph-{index}"
                    ),
                    "paragraph": index,
                },
                "style": (
                    paragraph.style.name
                    if paragraph.style is not None
                    else None
                ),
                "text": text,
            }
        )

    tables = []

    for table_index, table in enumerate(
        document.tables,
        start=1,
    ):
        rows = []

        for row_index, row in enumerate(
            table.rows,
            start=1,
        ):
            rows.append(
                {
                    "row": row_index,
                    "source_ref": {
                        "file": path.name,
                        "locator": (
                            f"{path.name}#"
                            f"table-{table_index}-"
                            f"row-{row_index}"
                        ),
                        "table": table_index,
                        "row": row_index,
                    },
                    "cells": [
                        cell.text.strip()
                        for cell in row.cells
                    ],
                }
            )

        tables.append(
            {
                "index": table_index,
                "rows": rows,
            }
        )

    return NormalizedArtifact(
        artifact_type=artifact_type,
        source_file=path.name,
        source_sha256=sha256_file(path),
        extractor="docx-structural-v1",
        schema_version="1.0",
        content={
            "paragraphs": paragraphs,
            "tables": tables,
        },
    )
