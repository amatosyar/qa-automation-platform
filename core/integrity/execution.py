"""Execution Integrity Engine.

Correlaciona de forma determinística:

Result
+ Evidence
+ Traceability

para impedir que evidencia válida de otra ejecución sea utilizada
para aprobar un caso.
"""

from __future__ import annotations

import json
from pathlib import Path

from core.common.exceptions import EvidenceError
from core.evidence import validate_manifest
from core.paths import (
    evidence_manifest_ref,
    result_path,
    result_ref,
)
from core.traceability import read_case


def _read_result(path: Path) -> dict:
    if not path.is_file():
        raise EvidenceError(
            f"No existe result.json: {path}"
        )

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as exc:
        raise EvidenceError(
            f"Result inválido: {path}"
        ) from exc


def validate_execution_integrity(
    *,
    results_root: Path,
    evidence_root: Path,
    traceability_root: Path,
    run_id: str,
    case_id: str,
    attempt: int,
    evidence_requirement=None,
) -> dict:
    findings: list[str] = []

    persisted_result_path = result_path(
        results_root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
    )

    result = _read_result(
        persisted_result_path
    )

    if result.get("run_id") != run_id:
        findings.append("result_run_id_mismatch")

    if result.get("case_id") != case_id:
        findings.append("result_case_id_mismatch")

    if result.get("attempt") != attempt:
        findings.append("result_attempt_mismatch")

    traceability = read_case(
        traceability_root,
        case_id,
    )

    if traceability is None:
        findings.append(
            "traceability_case_missing"
        )
    else:
        expected_result_ref = result_ref(
            run_id=run_id,
            case_id=case_id,
            attempt=attempt,
        )

        if expected_result_ref not in traceability.get(
            "execution_refs",
            [],
        ):
            findings.append(
                "traceability_execution_ref_mismatch"
            )

        expected_manifest_ref = evidence_manifest_ref(
            run_id=run_id,
            case_id=case_id,
            attempt=attempt,
        )

        if expected_manifest_ref not in traceability.get(
            "evidence_refs",
            [],
        ):
            findings.append(
                "traceability_evidence_ref_mismatch"
            )

    evidence = validate_manifest(
        evidence_root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
        requirement=evidence_requirement,
    )

    if not evidence["complete"]:
        findings.extend(
            f"evidence_{finding}"
            for finding
            in evidence["findings"]
        )

    return {
        "run_id": run_id,
        "case_id": case_id,
        "attempt": attempt,
        "valid": not findings,
        "findings": findings,
        "result_path": str(persisted_result_path),
        "manifest_path": evidence["manifest"],
    }
