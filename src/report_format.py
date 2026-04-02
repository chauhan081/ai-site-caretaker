from __future__ import annotations

from .models import CheckResult
from .severity import infer_severity, summarize_overall_severity



def render_report_summary(results: list[CheckResult]) -> str:
    overall = summarize_overall_severity(results)
    lines = [f'Overall severity: {overall.upper()}', '']
    for result in results:
        severity = infer_severity(result)
        status = 'OK' if result.ok else 'FAIL'
        lines.append(f'- [{status}] {result.name} | severity={severity} | {result.summary}')
    return '\n'.join(lines)
