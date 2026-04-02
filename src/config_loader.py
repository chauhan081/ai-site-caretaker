from __future__ import annotations

import json
from pathlib import Path

from .models import TargetConfig


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config' / 'targets.json'
EXAMPLE_CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config' / 'targets.example.json'



def load_targets(path: Path | None = None) -> list[TargetConfig]:
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return []
    payload = json.loads(config_path.read_text(encoding='utf-8'))
    targets = payload.get('targets', [])
    return [TargetConfig(**target) for target in targets]
