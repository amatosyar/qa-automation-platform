from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DiscoveryStatus(str, Enum):
    VERIFIED = "VERIFIED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"


@dataclass(frozen=True)
class LocatorEvidence:
    strategy: str
    value: str
    match_count: int
    source: str = "DOM_INSPECTION"

    def __post_init__(self) -> None:
        if not self.strategy.strip():
            raise ValueError("strategy is required")

        if not self.value.strip():
            raise ValueError("value is required")

        if self.match_count < 0:
            raise ValueError("match_count cannot be negative")

        if self.source != "DOM_INSPECTION":
            raise ValueError(
                "locator evidence must originate from DOM_INSPECTION"
            )

    @property
    def status(self) -> DiscoveryStatus:
        if self.match_count == 0:
            return DiscoveryStatus.NOT_FOUND

        if self.match_count == 1:
            return DiscoveryStatus.VERIFIED

        return DiscoveryStatus.AMBIGUOUS


@dataclass(frozen=True)
class DiscoveryElement:
    name: str
    page_url: str
    locator: LocatorEvidence
    role: str | None = None
    accessible_name: str | None = None
    label: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")

        if not self.page_url.strip():
            raise ValueError("page_url is required")

    @property
    def verified(self) -> bool:
        return self.locator.status is DiscoveryStatus.VERIFIED
