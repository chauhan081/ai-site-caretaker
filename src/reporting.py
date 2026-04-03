from __future__ import annotations

from .checks import check_server, check_site, check_ssl
from .logs import read_logs
from .models import CheckResult, TargetConfig


DEFAULT_CHECKS = ['site', 'ssl', 'server']



def build_daily_report(target: TargetConfig) -> list[CheckResult]:
    results: list[CheckResult] = []
    requested_checks = target.checks or DEFAULT_CHECKS

    if 'site' in requested_checks and target.url:
        results.append(check_site(target.url))

    if 'ssl' in requested_checks and (target.url or target.host):
        results.append(check_ssl(target.url or target.host or ''))

    if 'server' in requested_checks and target.host:
        ports = target.server_ports or [80]
        for port in ports:
            result = check_server(target.host, port=port)
            result.details.setdefault('target_check', 'server')
            result.name = f'check-server:{port}'
            results.append(result)

    if 'logs' in requested_checks:
        for log_path in target.log_paths:
            result = read_logs(log_path, lines=50)
            result.details.setdefault('target_check', 'logs')
            result.name = f'read-logs:{log_path}'
            results.append(result)

    return results
