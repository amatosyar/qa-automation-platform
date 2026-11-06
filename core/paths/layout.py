"""Rutas canónicas de QA Automation Platform.

Ningún componente debe reconstruir manualmente rutas persistentes
cuando exista una función canónica en este módulo.
"""

from __future__ import annotations

from pathlib import Path


def result_path(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> Path:
    return (
        root
        / "results"
        / run_id
        / case_id
        / str(attempt)
        / "result.json"
    )


def result_ref(
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> str:
    return (
        f"results/{run_id}/"
        f"{case_id}/{attempt}/result.json"
    )


def evidence_attempt_dir(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> Path:
    return (
        root
        / run_id
        / case_id
        / str(attempt)
    )


def evidence_manifest_path(
    root: Path,
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> Path:
    return (
        evidence_attempt_dir(
            root,
            run_id=run_id,
            case_id=case_id,
            attempt=attempt,
        )
        / "manifest.json"
    )


def evidence_manifest_ref(
    *,
    run_id: str,
    case_id: str,
    attempt: int,
) -> str:
    return (
        f"evidence/{run_id}/"
        f"{case_id}/{attempt}/manifest.json"
    )


def traceability_case_path(
    root: Path,
    *,
    case_id: str,
) -> Path:
    return (
        root
        / "cases"
        / f"{case_id}.json"
    )
