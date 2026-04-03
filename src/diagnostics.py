from __future__ import annotations

from .models import CheckResult, DiagnosisReport
from .severity import summarize_overall_severity


FAILURE_HINTS = {
    'check-site': 'Website availability issue. Inspect HTTP status, DNS, upstream app, or reverse proxy.',
    'check-ssl': 'SSL issue. Check certificate expiry, DNS, port 443 exposure, and certificate renewal jobs.',
    'check-server': 'Network reachability issue. Verify host resolution, firewall rules, server uptime, and listening port.',
    'read-logs': 'Application log issue. Review error-like lines and correlate with recent deploys or config changes.',
}



def _base_name(result_name: str) -> str:
    if ':' in result_name:
        return result_name.split(':', 1)[0]
    return result_name



def build_diagnosis(results: list[CheckResult]) -> DiagnosisReport:
    if not results:
        return DiagnosisReport(
            healthy=True,
            summary='No checks matched the alert filters.',
            overall_severity='info',
        )

    failures = [result for result in results if not result.ok]
    healthy = len(failures) == 0
    probable_causes: list[str] = []
    recommended_actions: list[str] = []

    for result in failures:
        base_name = _base_name(result.name)
        probable_causes.append(FAILURE_HINTS.get(base_name, f'Failure detected in {result.name}.'))
        if base_name == 'check-site':
            recommended_actions.extend([
                'Retry the endpoint manually and confirm expected status code.',
                'Check application logs around the failed request window.',
            ])
        elif base_name == 'check-ssl':
            recommended_actions.extend([
                'Inspect certificate expiry and auto-renew configuration.',
                'Confirm the correct certificate is served for the hostname.',
            ])
        elif base_name == 'check-server':
            recommended_actions.extend([
                'Verify firewall/security-group rules for the target port.',
                'Check whether the service is listening on the expected interface.',
            ])
        elif base_name == 'read-logs':
            recommended_actions.extend([
                'Review the latest error-like log lines for stack traces or repeating failures.',
                'Compare recent deploys, env changes, and dependency updates.',
            ])

    summary = 'All monitored checks look healthy.' if healthy else f'{len(failures)} check(s) need attention.'
    return DiagnosisReport(
        healthy=healthy,
        summary=summary,
        failed_checks=[result.name for result in failures],
        probable_causes=probable_causes,
        recommended_actions=list(dict.fromkeys(recommended_actions)),
        overall_severity=summarize_overall_severity(results),
    )
