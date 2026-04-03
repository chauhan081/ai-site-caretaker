from __future__ import annotations

from .models import TargetConfig
from .severity import SEVERITY_ORDER


ALLOWED_CHECKS = {'site', 'ssl', 'server', 'logs'}
ALLOWED_NOTIFICATION_TYPES = {'email', 'webhook', 'stdout', 'slack'}



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
    seen_notification_names: set[str] = set()
    for notification_target in target.notification_targets:
        if not notification_target.name:
            errors.append('Notification targets require a name.')
        elif notification_target.name in seen_notification_names:
            errors.append(f'Duplicate notification target name: {notification_target.name}.')
        else:
            seen_notification_names.add(notification_target.name)
        if notification_target.type not in ALLOWED_NOTIFICATION_TYPES:
            errors.append(
                f"Unsupported notification target type for {notification_target.name or '<unnamed>'}: {notification_target.type}."
            )
        if not notification_target.destination:
            errors.append(f'Notification target {notification_target.name or "<unnamed>"} requires a destination.')
        if notification_target.min_severity is not None and notification_target.min_severity not in SEVERITY_ORDER:
            errors.append(
                f"Notification target {notification_target.name or '<unnamed>'} has invalid min_severity: {notification_target.min_severity}."
            )
    return errors
