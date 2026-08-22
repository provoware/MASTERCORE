"""Stable, serializable contracts for the project start routine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum


class EventStatus(StrEnum):
    INFO = "INFO"
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class StartupEvent:
    """One human-readable and machine-readable workflow observation."""

    status: EventStatus
    step: str
    message: str
    solution: str = ""
    details: str = ""
    timestamp: str = ""

    def to_json(self) -> str:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["timestamp"] = self.timestamp or datetime.now(UTC).isoformat()
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
