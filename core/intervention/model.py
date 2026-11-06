"""Contrato persistente para intervención humana."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

from core.common.enums import InterventionAction


@dataclass(frozen=True)
class InterventionRecord:
    case_id: str
    attempted: str
    found: str
    needed: str
    action: InterventionAction
    observation: str | None = None
    evidence_refs: tuple[str, ...] = ()
    timestamp: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["action"] = self.action.value
        data["evidence_refs"] = list(self.evidence_refs)
        return data


def create_record(
    *,
    case_id: str,
    attempted: str,
    found: str,
    needed: str,
    action: InterventionAction,
    observation: str | None = None,
    evidence_refs: list[str] | None = None,
) -> InterventionRecord:
    return InterventionRecord(
        case_id=case_id,
        attempted=attempted,
        found=found,
        needed=needed,
        action=action,
        observation=observation,
        evidence_refs=tuple(evidence_refs or []),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def save_record(root: Path, record: InterventionRecord) -> Path:
    directory = root / "interventions"
    directory.mkdir(parents=True, exist_ok=True)

    safe_timestamp = (
        record.timestamp
        .replace(":", "-")
        .replace("+", "_")
    )

    path = directory / f"{record.case_id}_{safe_timestamp}.json"

    path.write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return path
