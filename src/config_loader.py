from __future__ import annotations

import json
from pathlib import Path

from .models import NotificationTarget, TargetConfig


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config' / 'targets.json'
EXAMPLE_CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config' / 'targets.example.json'



def load_targets(path: Path | None = None) -> list[TargetConfig]:
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return []
    payload = json.loads(config_path.read_text(encoding='utf-8'))
    targets = payload.get('targets', [])
    normalized_targets: list[TargetConfig] = []
    for target in targets:
        normalized = dict(target)
        normalized.setdefault('checks', [])
        normalized.setdefault('server_ports', [])
        normalized.setdefault('log_paths', [])
        notification_targets = []
        for notification_target in normalized.get('notification_targets', []):
            notification_targets.append(NotificationTarget(**notification_target))
        normalized['notification_targets'] = notification_targets
        normalized_targets.append(TargetConfig(**normalized))
    return normalized_targets
