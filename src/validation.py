from __future__ import annotations

from .models import TargetConfig


ALLOWED_CHECKS = {'site', 'ssl', 'server', 'logs'}



def validate_target(target: TargetConfig) -> list[str]:
    errors: list[str] = []
    if not target.name:
        errors.append('Target name is required.')
    if not target.url and not target.host and not target.log_paths:
        errors.append('At least one of url, host, or log_paths must be provided.')
    if target.url and not (target.url.startswith('http://') or target.url.startswith('https://')):
        errors.append('Target url must start with http:// or https://.')
    invalid_checks = [check for check in target.checks if check not in ALLOWED_CHECKS]
    if invalid_checks:
        errors.append(f"Unsupported checks requested: {', '.join(invalid_checks)}.")
    if any(port <= 0 or port > 65535 for port in target.server_ports):
        errors.append('Server ports must be between 1 and 65535.')
    if 'site' in target.checks and not target.url:
        errors.append('The site check requires target.url.')
    if 'ssl' in target.checks and not (target.url or target.host):
        errors.append('The ssl check requires target.url or target.host.')
    if 'server' in target.checks and not target.host:
        errors.append('The server check requires target.host.')
    if 'logs' in target.checks and not target.log_paths:
        errors.append('The logs check requires at least one log path.')
    return errors
