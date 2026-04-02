from __future__ import annotations

from .models import CheckResult, DiagnosisReport


FAILURE_HINTS = {
    'check-site': 'Website availability issue. Inspect HTTP status, DNS, upstream app, or reverse proxy.',
    'check-ssl': 'SSL issue. Check certificate expiry, DNS, port 443 exposure, and certificate renewal jobs.',
    'check-server': 'Network reachability issue. Verify host resolution, firewall rules, server uptime, and listening port.',
    'read-logs': 'Application log issue. Review error-like lines and correlate with recent deploys or config changes.',
}



def build_diagnosis(results: list[CheckResult]) -> DiagnosisReport:
    failures = [result for result in results if not result.ok]
    healthy = len(failures) == 0
    probable_causes: list[str] = []
    recommended_actions: list[str] = []

    for result in failures:
        probable_causes.append(FAILURE_HINTS.get(result.name, f'Failure detected in {result.name}.'))
        if result.name == 'check-site':
            recommended_actions.extend([
                'Retry the endpoint manually and confirm expected status code.',
                'Check application logs around the failed request window.',
            ])
        elif result.name == 'check-ssl':
            recommended_actions.extend([
                'Inspect certificate expiry and auto-renew configuration.',
                'Confirm the correct certificate is served for the hostname.',
            ])
        elif result.name == 'check-server':
            recommended_actions.extend([
                'Verify firewall/security-group rules for the target port.',
                'Check whether the service is listening on the expected interface.',
            ])
        elif result.name == 'read-logs':
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
    )
