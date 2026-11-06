"""Modelos normalizados de artefactos fuente."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ArtifactType(str, Enum):
    MATRIX = "MATRIX"
    EF = "EF"
    ET = "ET"


@dataclass(frozen=True)
class SourceReference:
    file: str
    locator: str
    sheet: str | None = None
    row: int | None = None
    section: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class NormalizedArtifact:
    artifact_type: ArtifactType
    source_file: str
    source_sha256: str
    extractor: str
    schema_version: str
    content: dict[str, Any]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["artifact_type"] = self.artifact_type.value
        data["warnings"] = list(self.warnings)
        return data


def relative_source(path: Path, base: Path | None = None) -> str:
    if base is None:
        return path.name

    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path.resolve())
