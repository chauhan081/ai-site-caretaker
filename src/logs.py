from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .models import CheckResult


_ERROR_KEYWORDS = ('error', 'fail', 'exception', 'critical', 'panic', 'fatal', 'traceback')
_WARNING_KEYWORDS = ('warn', 'timeout', 'retry', 'refused', 'denied', 'slow')
_IGNORED_ERROR_PHRASES = ('0 errors', 'without errors', 'no errors detected')
_PREFIX_RE = re.compile(
    r'^(?:\d{4}-\d{2}-\d{2}[tT ][^\s]+|\[[^\]]+\]|\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}|\d{2}:\d{2}:\d{2})\s*'
)



def _classify_line(line: str) -> str | None:
    normalized = line.lower()
    if any(phrase in normalized for phrase in _IGNORED_ERROR_PHRASES):
        return None
    if any(keyword in normalized for keyword in _ERROR_KEYWORDS):
        return 'error'
    if any(keyword in normalized for keyword in _WARNING_KEYWORDS):
        return 'warning'
    if ' info ' in f' {normalized} ':
        return 'info'
    return None



def _normalize_pattern(line: str) -> str:
    pattern = _PREFIX_RE.sub('', line.strip())
    pattern = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '<ip>', pattern)
    pattern = re.sub(r'\b[0-9a-f]{8,}\b', '<id>', pattern, flags=re.IGNORECASE)
    pattern = re.sub(r'\b\d+\b', '<n>', pattern)
    pattern = re.sub(r'"[^"]*"', '"<value>"', pattern)
    pattern = re.sub(r"'[^']*'", "'<value>'", pattern)
    pattern = re.sub(r'\s+', ' ', pattern)
    return pattern[:160]



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

    severities = Counter()
    matches: list[dict[str, str | int]] = []
    patterns = Counter()

    for index, line in enumerate(tail, start=max(1, len(content) - len(tail) + 1)):
        severity = _classify_line(line)
        if severity is None:
            continue
        severities[severity] += 1
        if severity in {'error', 'warning'}:
            patterns[_normalize_pattern(line)] += 1
        matches.append({'line_number': index, 'severity': severity, 'message': line})

    error_like_lines = severities['error']
    warning_like_lines = severities['warning']
    recurring_patterns = [
        {'pattern': pattern, 'count': count}
        for pattern, count in patterns.most_common(5)
    ]
    sample_matches = matches[-5:]

    summary_bits = [f'Read {len(tail)} line(s) from {log_path}']
    if error_like_lines:
        summary_bits.append(f'{error_like_lines} error-like line(s)')
    if warning_like_lines:
        summary_bits.append(f'{warning_like_lines} warning-like line(s)')
    if recurring_patterns:
        top_pattern = recurring_patterns[0]
        summary_bits.append(f"top recurring pattern: {top_pattern['pattern']} ({top_pattern['count']}x)")

    return CheckResult(
        name='read-logs',
        ok=error_like_lines == 0,
        summary='; '.join(summary_bits),
        details={
            'path': str(log_path),
            'lines_read': len(tail),
            'error_like_lines': error_like_lines,
            'warning_like_lines': warning_like_lines,
            'severity_counts': dict(severities),
            'recurring_patterns': recurring_patterns,
            'sample_matches': sample_matches,
            'preview': '\n'.join(tail[-10:]),
        },
    )
