from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


SUPPORTED_EXPORT_FORMATS = {'.json', '.txt'}


def export_text(content: str, destination: str | Path) -> Path:
    path = Path(destination)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(f'Unsupported export format: {suffix or "<none>"}. Use .txt or .json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + ('\n' if not content.endswith('\n') else ''), encoding='utf-8')
    return path


def resolve_export_path(
    *,
    command_name: str,
    target_name: str,
    as_json: bool,
    output_path: str | None = None,
    output_dir: str | Path | None = None,
    timestamped: bool = False,
    alerts_only: bool = False,
    min_severity: str | None = None,
    now: datetime | None = None,
) -> Path | None:
    if output_path and output_dir:
        raise ValueError('Use either --output or --output-dir, not both')

    suffix = '.json' if as_json else '.txt'
    timestamp_value = (now or datetime.now()).strftime('%Y%m%d-%H%M%S')

    if output_path:
        path = Path(output_path)
        if timestamped:
            if path.suffix.lower() not in SUPPORTED_EXPORT_FORMATS:
                raise ValueError(f'Unsupported export format: {path.suffix.lower() or "<none>"}. Use .txt or .json')
            path = path.with_name(f'{path.stem}-{timestamp_value}{path.suffix}')
        return path

    if not output_dir:
        return None

    safe_target = _slugify(target_name)
    safe_command = _slugify(command_name)
    parts = [safe_target, safe_command]
    if alerts_only:
        parts.append('alerts')
    if min_severity:
        parts.extend(['min', _slugify(min_severity)])
    if timestamped:
        parts.append(timestamp_value)
    filename = '-'.join(parts) + suffix
    return Path(output_dir) / filename


def _slugify(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    return slug or 'export'
