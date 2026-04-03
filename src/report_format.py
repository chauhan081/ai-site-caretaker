from __future__ import annotations

import json
from typing import Any

from .models import CheckResult
from .output import serialize_result
from .severity import infer_severity, summarize_overall_severity



def serialize_report_summary(results: list[CheckResult]) -> dict[str, Any]:
    return {
        'overall_severity': summarize_overall_severity(results),
        'results': [serialize_result(result) for result in results],
    }



def render_report_summary(results: list[CheckResult], as_json: bool = False) -> str:
    payload = serialize_report_summary(results)
    if as_json:
        return json.dumps(payload, indent=2)

    overall = payload['overall_severity']
    lines = [f'Overall severity: {overall.upper()}', '']
    for result in results:
        severity = infer_severity(result)
        status = 'OK' if result.ok else 'FAIL'
        lines.append(f'- [{status}] {result.name} | severity={severity} | {result.summary}')
    return '\n'.join(lines)
