from __future__ import annotations

import json
from typing import Any

from .models import CheckResult, DiagnosisReport
from .severity import infer_severity



def serialize_result(result: CheckResult) -> dict[str, Any]:
    return {
        'name': result.name,
        'ok': result.ok,
        'summary': result.summary,
        'details': result.details,
        'severity': infer_severity(result),
    }



def serialize_diagnosis(report: DiagnosisReport) -> dict[str, Any]:
    return {
        'healthy': report.healthy,
        'summary': report.summary,
        'failed_checks': report.failed_checks,
        'probable_causes': report.probable_causes,
        'recommended_actions': report.recommended_actions,
        'overall_severity': report.overall_severity,
    }



def render_result(result: CheckResult, as_json: bool = False) -> str:
    payload = serialize_result(result)
    if as_json:
        return json.dumps(payload, indent=2)

    status = 'OK' if result.ok else 'FAIL'
    severity = payload['severity']
    lines = [f'[{status}] {result.name} ({severity})', result.summary]
    if result.details:
        lines.append('')
        lines.append('Details:')
        for key, value in result.details.items():
            lines.append(f'- {key}: {value}')
    return '\n'.join(lines)



def render_diagnosis(report: DiagnosisReport, as_json: bool = False) -> str:
    payload = serialize_diagnosis(report)
    if as_json:
        return json.dumps(payload, indent=2)

    status = 'HEALTHY' if report.healthy else 'ATTENTION NEEDED'
    lines = [f'[{status}] Diagnosis', report.summary, f'Overall severity: {report.overall_severity.upper()}']
    if report.failed_checks:
        lines.append('')
        lines.append('Failed checks:')
        for item in report.failed_checks:
            lines.append(f'- {item}')
    if report.probable_causes:
        lines.append('')
        lines.append('Probable causes:')
        for item in report.probable_causes:
            lines.append(f'- {item}')
    if report.recommended_actions:
        lines.append('')
        lines.append('Recommended actions:')
        for item in report.recommended_actions:
            lines.append(f'- {item}')
    return '\n'.join(lines)
