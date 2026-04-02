from __future__ import annotations

from pathlib import Path

from .models import CheckResult



def read_logs(path: str, lines: int = 50) -> CheckResult:
    log_path = Path(path)
    if not log_path.exists():
        return CheckResult(
            name='read-logs',
            ok=False,
            summary=f'Log file not found: {log_path}',
            details={'path': str(log_path)},
        )

    content = log_path.read_text(encoding='utf-8', errors='replace').splitlines()
    tail = content[-lines:] if lines > 0 else content
    error_lines = [line for line in tail if any(word in line.lower() for word in ('error', 'fail', 'exception', 'critical'))]
    return CheckResult(
        name='read-logs',
        ok=True,
        summary=f'Read {len(tail)} line(s) from {log_path}',
        details={
            'path': str(log_path),
            'lines_read': len(tail),
            'error_like_lines': len(error_lines),
            'preview': '\n'.join(tail[-10:]),
        },
    )
