"""Normalización de Matriz + EF + ET."""

from __future__ import annotations

from pathlib import Path

from core.artifacts.adapters.docx import extract_docx
from core.artifacts.adapters.matrix import extract_matrix
from core.artifacts.io import write_json
from core.artifacts.models.artifact import ArtifactType
from core.common.exceptions import ArtifactError


REQUIRED_FILENAMES = {
    ArtifactType.MATRIX: "matrix.normalized.json",
    ArtifactType.EF: "ef.normalized.json",
    ArtifactType.ET: "et.normalized.json",
}


def normalize_artifacts(
    *,
    matrix: Path,
    ef: Path,
    et: Path,
    output_dir: Path,
) -> dict[str, Path]:
    """Normalizar los tres artefactos obligatorios."""

    missing = [
        str(path)
        for path in (matrix, ef, et)
        if not path.is_file()
    ]

    if missing:
        raise ArtifactError(
            "Faltan artefactos obligatorios: "
            + ", ".join(missing)
        )

    artifacts = {
        ArtifactType.MATRIX: extract_matrix(
            matrix
        ),
        ArtifactType.EF: extract_docx(
            ef,
            ArtifactType.EF,
        ),
        ArtifactType.ET: extract_docx(
            et,
            ArtifactType.ET,
        ),
    }

    outputs = {}

    for artifact_type, artifact in artifacts.items():
        output = (
            output_dir
            / REQUIRED_FILENAMES[artifact_type]
        )

        write_json(
            output,
            artifact.to_dict(),
        )

        outputs[
            artifact_type.value
        ] = output

    return outputs
