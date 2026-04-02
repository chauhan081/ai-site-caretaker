from __future__ import annotations

from .checks import check_server, check_site, check_ssl
from .models import CheckResult, TargetConfig



def build_daily_report(target: TargetConfig) -> list[CheckResult]:
    results: list[CheckResult] = []
    if target.url:
        results.append(check_site(target.url))
        results.append(check_ssl(target.url))
    if target.host:
        results.append(check_server(target.host, port=80))
    return results
