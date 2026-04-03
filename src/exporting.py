from __future__ import annotations

from pathlib import Path


SUPPORTED_EXPORT_FORMATS = {'.json', '.txt'}


def export_text(content: str, destination: str | Path) -> Path:
    path = Path(destination)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(f'Unsupported export format: {suffix or "<none>"}. Use .txt or .json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + ('\n' if not content.endswith('\n') else ''), encoding='utf-8')
    return path
