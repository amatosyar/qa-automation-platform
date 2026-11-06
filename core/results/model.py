"""Modelo de resultado por ejecución e intento."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

from core.common.enums import ExecutionStatus


@dataclass(frozen=True)
class ExecutionResult:
    run_id: str
    case_id: str
    attempt: int
    status: ExecutionStatus
    duration_ms: int
    environment: str | None
    browser: str | None
    evidence_refs: tuple[str, ...]
    error: str | None
    timestamp: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["evidence_refs"] = list(self.evidence_refs)
        return data


def create_result(
    *,
    run_id: str,
    case_id: str,
    attempt: int,
    status: ExecutionStatus,
    duration_ms: int,
    environment: str | None = None,
    browser: str | None = None,
    evidence_refs: list[str] | None = None,
    error: str | None = None,
) -> ExecutionResult:
    return ExecutionResult(
        run_id=run_id,
        case_id=case_id,
        attempt=attempt,
        status=status,
        duration_ms=duration_ms,
        environment=environment,
        browser=browser,
        evidence_refs=tuple(evidence_refs or []),
        error=error,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def save_result(root: Path, result: ExecutionResult) -> Path:
    directory = (
        root
        / "results"
        / result.run_id
        / result.case_id
        / str(result.attempt)
    )

    directory.mkdir(parents=True, exist_ok=True)

    path = directory / "result.json"

    path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return path
