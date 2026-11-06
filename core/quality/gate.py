"""Quality Gate determinístico.

El Reviewer puede emitir PASS, pero el framework decide si el caso
realmente puede finalizar.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.common.enums import ExecutionStatus, ReviewStatus


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

