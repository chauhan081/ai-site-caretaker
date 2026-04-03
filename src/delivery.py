from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import request

from .models import CheckResult, NotificationTarget
from .severity import SEVERITY_ORDER, summarize_overall_severity


class DeliveryError(RuntimeError):
    pass


def should_deliver(results: list[CheckResult], delivery_target: NotificationTarget | None) -> bool:
    if delivery_target is None:
        return False
    if not delivery_target.enabled:
        return False
    if delivery_target.min_severity is None:
        return True
    overall_severity = summarize_overall_severity(results)
    return SEVERITY_ORDER.index(overall_severity) >= SEVERITY_ORDER.index(delivery_target.min_severity)


def deliver_notification(
    rendered_content: str,
    *,
    delivery_target: NotificationTarget,
    as_json: bool,
    source_command: str,
    monitored_target: str,
) -> str:
    target_type = delivery_target.type
    if target_type == 'stdout':
        return _deliver_stdout(rendered_content, delivery_target)
    if target_type == 'file':
        return _deliver_file(rendered_content, delivery_target)
    if target_type in {'webhook', 'slack'}:
        return _deliver_webhook(
            rendered_content,
            delivery_target=delivery_target,
            as_json=as_json,
            source_command=source_command,
            monitored_target=monitored_target,
        )
    if target_type == 'email':
        raise DeliveryError('Email delivery is not implemented yet. Use --notify-format without --deliver for metadata-only output.')
    raise DeliveryError(f'Unsupported delivery target type: {target_type}')


def _deliver_stdout(rendered_content: str, delivery_target: NotificationTarget) -> str:
    stream_name = delivery_target.destination.strip().lower() or 'stdout'
    if stream_name not in {'stdout', 'stderr'}:
        raise DeliveryError("Stdout delivery destination must be 'stdout' or 'stderr'.")
    print(rendered_content)
    return f'Delivered notification to {delivery_target.name} ({stream_name})'


def _deliver_file(rendered_content: str, delivery_target: NotificationTarget) -> str:
    destination = Path(delivery_target.destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered_content + ('\n' if not rendered_content.endswith('\n') else ''), encoding='utf-8')
    return f'Delivered notification to {delivery_target.name} ({destination})'


def _deliver_webhook(
    rendered_content: str,
    *,
    delivery_target: NotificationTarget,
    as_json: bool,
    source_command: str,
    monitored_target: str,
) -> str:
    payload: dict[str, Any]
    if delivery_target.type == 'slack':
        payload = {
            'text': rendered_content,
            'metadata': {
                'source_command': source_command,
                'target': monitored_target,
            },
        }
    elif as_json:
        payload = json.loads(rendered_content)
    else:
        payload = {
            'text': rendered_content,
            'source_command': source_command,
            'target': monitored_target,
        }
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        delivery_target.destination,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            status = getattr(response, 'status', response.getcode())
    except Exception as exc:  # pragma: no cover - exercised via tests with mocking
        raise DeliveryError(f'Webhook delivery failed for {delivery_target.name}: {exc}') from exc
    if status < 200 or status >= 300:
        raise DeliveryError(f'Webhook delivery failed for {delivery_target.name}: HTTP {status}')
    return f'Delivered notification to {delivery_target.name} (HTTP {status})'
