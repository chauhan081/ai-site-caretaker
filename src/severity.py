from __future__ import annotations

from .models import CheckResult


SEVERITY_ORDER = ('info', 'low', 'medium', 'high', 'critical')



def infer_severity(result: CheckResult) -> str:
    if result.ok:
        return 'info'
    if result.name == 'check-ssl':
        days_left = result.details.get('days_left')
        if isinstance(days_left, int):
            if days_left <= 3:
                return 'critical'
            if days_left <= 7:
                return 'high'
            return 'medium'
        return 'high'
    if result.name == 'check-site':
        status = result.details.get('status')
        if isinstance(status, int) and status >= 500:
            return 'critical'
        return 'high'
    if result.name == 'check-server':
        return 'high'
    if result.name == 'read-logs':
        errors = result.details.get('error_like_lines', 0)
        if isinstance(errors, int) and errors >= 10:
            return 'critical'
        if isinstance(errors, int) and errors >= 3:
            return 'high'
        return 'medium'
    return 'medium'



def summarize_overall_severity(results: list[CheckResult]) -> str:
    severities = [infer_severity(result) for result in results]
    highest = 'info'
    for severity in severities:
        if SEVERITY_ORDER.index(severity) > SEVERITY_ORDER.index(highest):
            highest = severity
    return highest
