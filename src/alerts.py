from __future__ import annotations

from .models import CheckResult
from .severity import SEVERITY_ORDER, infer_severity


VALID_ALERT_SEVERITIES = tuple(level for level in SEVERITY_ORDER if level != 'info')


def filter_results(
    results: list[CheckResult],
    *,
    alerts_only: bool = False,
    min_severity: str | None = None,
) -> list[CheckResult]:
    threshold_index = None
    if min_severity is not None:
        threshold_index = SEVERITY_ORDER.index(min_severity)

    filtered: list[CheckResult] = []
    for result in results:
        severity = infer_severity(result)
        if alerts_only and result.ok:
            continue
        if threshold_index is not None and SEVERITY_ORDER.index(severity) < threshold_index:
            continue
        filtered.append(result)
    return filtered
