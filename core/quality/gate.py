"""Quality Gate determinístico.

El Reviewer puede emitir PASS, pero el framework decide si el caso
realmente puede finalizar.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.common.enums import ExecutionStatus, ReviewStatus
from core.paths import result_path


@dataclass(frozen=True)
class QualityGateInput:
    execution_status: ExecutionStatus
    review_status: ReviewStatus
    traceability_complete: bool
    evidence_complete: bool
    critical_findings: int = 0
    high_findings: int = 0


@dataclass(frozen=True)
class QualityGateResult:
    passed: bool
    reasons: tuple[str, ...]


def evaluate(data: QualityGateInput) -> QualityGateResult:
    reasons: list[str] = []

    if data.execution_status != ExecutionStatus.PASS:
        reasons.append(
            f"execution_status={data.execution_status.value}"
        )

    if data.review_status != ReviewStatus.PASS:
        reasons.append(
            f"review_status={data.review_status.value}"
        )

    if not data.traceability_complete:
        reasons.append("traceability_incomplete")

    if not data.evidence_complete:
        reasons.append("evidence_incomplete")

    if data.critical_findings > 0:
        reasons.append(
            f"critical_findings={data.critical_findings}"
        )

    if data.high_findings > 0:
        reasons.append(
            f"high_findings={data.high_findings}"
        )

    return QualityGateResult(
        passed=not reasons,
        reasons=tuple(reasons),
    )

def evaluate_case(
    *,
    traceability_root,
    case_id: str,
    execution_status: ExecutionStatus,
    review_status: ReviewStatus,
    evidence_complete: bool,
    critical_findings: int = 0,
    high_findings: int = 0,
    require_ef: bool = True,
    require_et: bool = True,
    require_knowledge: bool = False,
) -> QualityGateResult:
    """Evaluar un caso usando trazabilidad calculada por el Core.

    El caller no puede declarar manualmente que la trazabilidad está
    completa. El estado se obtiene del Traceability Engine.
    """

    from core.traceability import completeness

    traceability = completeness(
        traceability_root,
        case_id,
        require_ef=require_ef,
        require_et=require_et,
        require_knowledge=require_knowledge,
    )

    result = evaluate(
        QualityGateInput(
            execution_status=execution_status,
            review_status=review_status,
            traceability_complete=traceability["complete"],
            evidence_complete=evidence_complete,
            critical_findings=critical_findings,
            high_findings=high_findings,
        )
    )

    reasons = list(result.reasons)

    if not traceability["complete"]:
        for missing in traceability["missing"]:
            detail = f"traceability_missing={missing}"

            if detail not in reasons:
                reasons.append(detail)

    return QualityGateResult(
        passed=not reasons,
        reasons=tuple(reasons),
    )

def evaluate_case_with_evidence(
    *,
    traceability_root,
    evidence_root,
    run_id: str,
    case_id: str,
    attempt: int,
    execution_status: ExecutionStatus,
    review_status: ReviewStatus,
    critical_findings: int = 0,
    high_findings: int = 0,
    require_ef: bool = True,
    require_et: bool = True,
    require_knowledge: bool = False,
    evidence_requirement=None,
) -> QualityGateResult:
    """Quality Gate con Traceability y Evidence calculados por Core."""

    from core.evidence import (
        EvidenceRequirement,
        validate_manifest,
    )
    from core.traceability import completeness

    traceability = completeness(
        traceability_root,
        case_id,
        require_ef=require_ef,
        require_et=require_et,
        require_knowledge=require_knowledge,
    )

    requirement = (
        evidence_requirement
        if evidence_requirement is not None
        else EvidenceRequirement()
    )

    evidence = validate_manifest(
        evidence_root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
        requirement=requirement,
    )

    result = evaluate(
        QualityGateInput(
            execution_status=execution_status,
            review_status=review_status,
            traceability_complete=traceability["complete"],
            evidence_complete=evidence["complete"],
            critical_findings=critical_findings,
            high_findings=high_findings,
        )
    )

    reasons = list(result.reasons)

    if not traceability["complete"]:
        for missing in traceability["missing"]:
            detail = (
                f"traceability_missing={missing}"
            )

            if detail not in reasons:
                reasons.append(detail)

    if not evidence["complete"]:
        for finding in evidence["findings"]:
            detail = (
                f"evidence_{finding}"
            )

            if detail not in reasons:
                reasons.append(detail)

    return QualityGateResult(
        passed=not reasons,
        reasons=tuple(reasons),
    )

def evaluate_verified_case(
    *,
    traceability_root,
    evidence_root,
    results_root,
    run_id: str,
    case_id: str,
    attempt: int,
    review_status: ReviewStatus,
    critical_findings: int = 0,
    high_findings: int = 0,
    require_ef: bool = True,
    require_et: bool = True,
    require_knowledge: bool = False,
    evidence_requirement=None,
) -> QualityGateResult:
    """Quality Gate de máxima confianza.

    Execution, Traceability y Evidence se obtienen de evidencia
    persistida y verificaciones del Core.
    """

    import json

    from core.integrity import (
        validate_execution_integrity,
    )
    from core.traceability import completeness

    persisted_result_path = result_path(
        results_root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
    )

    if not persisted_result_path.is_file():
        return QualityGateResult(
            passed=False,
            reasons=("result_missing",),
        )

    try:
        result_data = json.loads(
            persisted_result_path.read_text(
                encoding="utf-8"
            )
        )
    except (json.JSONDecodeError, OSError):
        return QualityGateResult(
            passed=False,
            reasons=("result_invalid",),
        )

    try:
        execution_status = ExecutionStatus(
            result_data.get("status")
        )
    except (ValueError, TypeError):
        return QualityGateResult(
            passed=False,
            reasons=("result_status_invalid",),
        )

    traceability = completeness(
        traceability_root,
        case_id,
        require_ef=require_ef,
        require_et=require_et,
        require_knowledge=require_knowledge,
    )

    integrity = validate_execution_integrity(
        results_root=results_root,
        evidence_root=evidence_root,
        traceability_root=traceability_root,
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
        evidence_requirement=evidence_requirement,
    )

    reasons = []

    if execution_status != ExecutionStatus.PASS:
        reasons.append(
            f"execution_status="
            f"{execution_status.value}"
        )

    if review_status != ReviewStatus.PASS:
        reasons.append(
            f"review_status="
            f"{review_status.value}"
        )

    if not traceability["complete"]:
        reasons.append(
            "traceability_incomplete"
        )

        for missing in traceability["missing"]:
            reasons.append(
                f"traceability_missing={missing}"
            )

    if not integrity["valid"]:
        reasons.append(
            "execution_integrity_failed"
        )

        for finding in integrity["findings"]:
            reasons.append(
                f"integrity_{finding}"
            )

    if critical_findings > 0:
        reasons.append(
            f"critical_findings="
            f"{critical_findings}"
        )

    if high_findings > 0:
        reasons.append(
            f"high_findings="
            f"{high_findings}"
        )

    return QualityGateResult(
        passed=not reasons,
        reasons=tuple(reasons),
    )

