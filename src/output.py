from __future__ import annotations

import json

from .models import CheckResult



def render_result(result: CheckResult, as_json: bool = False) -> str:
    payload = {
        "name": result.name,
        "ok": result.ok,
        "summary": result.summary,
        "details": result.details,
    }
    if as_json:
        return json.dumps(payload, indent=2)

    status = "OK" if result.ok else "FAIL"
    lines = [f"[{status}] {result.name}", result.summary]
    if result.details:
        lines.append("")
        lines.append("Details:")
        for key, value in result.details.items():
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)
