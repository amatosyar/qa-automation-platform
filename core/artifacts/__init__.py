"""Artifact Engine."""

from core.artifacts.adapters.docx import extract_docx
from core.artifacts.adapters.matrix import extract_matrix
from core.artifacts.models.artifact import (
    ArtifactType,
    NormalizedArtifact,
    SourceReference,
)
from core.artifacts.normalizer import normalize_artifacts

__all__ = [
    "ArtifactType",
    "NormalizedArtifact",
    "SourceReference",
    "extract_docx",
    "extract_matrix",
    "normalize_artifacts",
]
