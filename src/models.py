from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    name: str
    ok: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetConfig:
    name: str
    url: str | None = None
    host: str | None = None
    notes: str | None = None
