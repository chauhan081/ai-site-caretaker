from __future__ import annotations

import json
from typing import Any

from .models import CheckResult, DiagnosisReport, NotificationTarget
from .output import serialize_diagnosis, serialize_result
from .severity import infer_severity, summarize_overall_severity


def resolve_notification_target(targets: list[NotificationTarget], name: str | None) -> NotificationTarget | None:
    if not name:
        return None
    for target in targets:
        if target.name == name:
            return target
    return None


def serialize_notification(
    monitored_target: str,
    results: list[CheckResult],
    *,
    diagnosis: DiagnosisReport | None = None,
    delivery_target: NotificationTarget | None = None,
    source_command: str,
) -> dict[str, Any]:
    overall_severity = diagnosis.overall_severity if diagnosis is not None else summarize_overall_severity(results)
    failures = [result for result in results if not result.ok]
    payload: dict[str, Any] = {
        'source_command': source_command,
        'target': monitored_target,
        'healthy': diagnosis.healthy if diagnosis is not None else len(failures) == 0,
        'overall_severity': overall_severity,
        'failure_count': len(failures),
        'alert_count': len(results),
        'results': [serialize_result(result) for result in results],
    }
    if delivery_target is not None:
        payload['delivery_target'] = {
            'name': delivery_target.name,
            'type': delivery_target.type,
            'destination': delivery_target.destination,
            'min_severity': delivery_target.min_severity,
            'enabled': delivery_target.enabled,
        }
    if diagnosis is not None:
        payload['diagnosis'] = serialize_diagnosis(diagnosis)
    return payload


def render_notification_text(
    monitored_target: str,
    results: list[CheckResult],
    *,
    diagnosis: DiagnosisReport | None = None,
    delivery_target: NotificationTarget | None = None,
    source_command: str,
) -> str:
    overall_severity = diagnosis.overall_severity if diagnosis is not None else summarize_overall_severity(results)
    status = 'OK' if (diagnosis.healthy if diagnosis is not None else all(result.ok for result in results)) else 'ALERT'
    lines = [f'[{status}] {monitored_target} | severity={overall_severity.upper()} | source={source_command}']
    if delivery_target is not None:
        lines.append(
            f"Delivery target: {delivery_target.name} ({delivery_target.type} -> {delivery_target.destination})"
        )

    if diagnosis is not None:
        lines.append(f'Diagnosis: {diagnosis.summary}')
    elif results:
        lines.append(f'{len(results)} result(s) matched the notification filter.')
    else:
        lines.append('No results matched the notification filter.')

    if not results:
        return '\n'.join(lines)

    lines.append('Alerts:')
    for result in results[:10]:
        severity = infer_severity(result).upper()
        outcome = 'OK' if result.ok else 'FAIL'
        lines.append(f'- [{outcome}] {severity} {result.name}: {result.summary}')

    if len(results) > 10:
        lines.append(f'- ... {len(results) - 10} more result(s) omitted')

    if diagnosis is not None and diagnosis.recommended_actions:
        lines.append('Recommended actions:')
        for action in diagnosis.recommended_actions[:3]:
            lines.append(f'- {action}')

    return '\n'.join(lines)


def render_notification_json(
    monitored_target: str,
    results: list[CheckResult],
    *,
    diagnosis: DiagnosisReport | None = None,
    delivery_target: NotificationTarget | None = None,
    source_command: str,
) -> str:
    return json.dumps(
        serialize_notification(
            monitored_target,
            results,
            diagnosis=diagnosis,
            delivery_target=delivery_target,
            source_command=source_command,
        ),
        indent=2,
    )
