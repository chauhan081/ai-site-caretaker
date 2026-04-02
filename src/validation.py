from __future__ import annotations

from .models import TargetConfig



def validate_target(target: TargetConfig) -> list[str]:
    errors: list[str] = []
    if not target.name:
        errors.append('Target name is required.')
    if not target.url and not target.host:
        errors.append('At least one of url or host must be provided.')
    if target.url and not (target.url.startswith('http://') or target.url.startswith('https://')):
        errors.append('Target url must start with http:// or https://.')
    return errors
