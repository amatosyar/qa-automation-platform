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
