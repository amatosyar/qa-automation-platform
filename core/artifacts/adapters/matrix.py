"""Extracción estructural de Matriz XLSX.

No interpreta semántica de negocio.
Preserva hojas, filas, columnas y coordenadas para trazabilidad.
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


def _load_openpyxl():
    try:
        import openpyxl
    except ImportError as exc:
        raise ArtifactError(
            "Se requiere openpyxl para procesar archivos XLSX."
        ) from exc

    return openpyxl


def extract_matrix(path: Path) -> NormalizedArtifact:
    openpyxl = _load_openpyxl()

    if path.suffix.lower() != ".xlsx":
        raise ArtifactError(
            f"La Matriz debe ser .xlsx: {path}"
        )

    try:
        workbook = openpyxl.load_workbook(
            path,
            read_only=True,
            data_only=True,
        )
    except (OSError, BadZipFile, ValueError) as exc:
        raise ArtifactError(
            f"No se pudo abrir la Matriz: {path}"
        ) from exc

    sheets = []

    try:
        for worksheet in workbook.worksheets:
            rows = []

            for row_number, cells in enumerate(
                worksheet.iter_rows(values_only=True),
                start=1,
            ):
                values = [
                    value
                    for value in cells
                ]

                if not any(
                    value is not None
                    and str(value).strip()
                    for value in values
                ):
                    continue

                rows.append(
                    {
                        "row": row_number,
                        "source_ref": {
                            "file": path.name,
                            "sheet": worksheet.title,
                            "row": row_number,
                            "locator": (
                                f"{path.name}#"
                                f"{worksheet.title}!R{row_number}"
                            ),
                        },
                        "values": values,
                    }
                )

            sheets.append(
                {
                    "name": worksheet.title,
                    "rows": rows,
                }
            )
    finally:
        workbook.close()

    return NormalizedArtifact(
        artifact_type=ArtifactType.MATRIX,
        source_file=path.name,
        source_sha256=sha256_file(path),
        extractor="xlsx-structural-v1",
        schema_version="1.0",
        content={
            "sheets": sheets,
        },
    )
