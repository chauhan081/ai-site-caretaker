from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NotificationTarget:
    name: str
    type: str
    destination: str
    min_severity: str | None = None
    enabled: bool = True


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
    checks: list[str] = field(default_factory=list)
    server_ports: list[int] = field(default_factory=list)
    log_paths: list[str] = field(default_factory=list)
    notification_targets: list[NotificationTarget] = field(default_factory=list)


@dataclass
class DiagnosisReport:
    healthy: bool
    summary: str
    failed_checks: list[str] = field(default_factory=list)
    probable_causes: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    overall_severity: str = 'info'
