"""IO determinístico para artefactos."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.common.exceptions import ArtifactError


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise ArtifactError(
            f"No existe el artefacto: {path}"
        )

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def write_json(path: Path, data: Any) -> Path:
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
