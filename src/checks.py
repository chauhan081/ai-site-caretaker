from __future__ import annotations

import socket
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

from .models import CheckResult


DEFAULT_TIMEOUT = 10


def check_site(url: str) -> CheckResult:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Site-Caretaker/0.1"})
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            status = getattr(response, "status", None) or response.getcode()
            final_url = response.geturl()
            ok = 200 <= status < 400
            return CheckResult(
                name="check-site",
                ok=ok,
                summary=f"HTTP {status} from {final_url}",
                details={"status": status, "final_url": final_url},
            )
    except urllib.error.HTTPError as exc:
        return CheckResult(
            name="check-site",
            ok=False,
            summary=f"HTTP error {exc.code} for {url}",
            details={"status": exc.code, "reason": str(exc)},
        )
    except Exception as exc:
        return CheckResult(
            name="check-site",
            ok=False,
            summary=f"Request failed for {url}",
            details={"error": str(exc)},
        )



def check_ssl(host_or_url: str, port: int = 443) -> CheckResult:
    host = _extract_host(host_or_url)
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=DEFAULT_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host) as secure_sock:
                cert = secure_sock.getpeercert()
        not_after = cert.get("notAfter")
        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        remaining = expiry - datetime.now(timezone.utc)
        days_left = remaining.days
        ok = days_left >= 15
        return CheckResult(
            name="check-ssl",
            ok=ok,
            summary=f"SSL valid for {days_left} day(s) on {host}",
            details={"host": host, "expires_at": expiry.isoformat(), "days_left": days_left},
        )
    except Exception as exc:
        return CheckResult(
            name="check-ssl",
            ok=False,
            summary=f"SSL check failed for {host}",
            details={"host": host, "error": str(exc)},
        )



def check_server(host: str, port: int = 80) -> CheckResult:
    try:
        with socket.create_connection((host, port), timeout=DEFAULT_TIMEOUT):
            return CheckResult(
                name="check-server",
                ok=True,
                summary=f"TCP connection to {host}:{port} succeeded",
                details={"host": host, "port": port},
            )
    except Exception as exc:
        return CheckResult(
            name="check-server",
            ok=False,
            summary=f"TCP connection to {host}:{port} failed",
            details={"host": host, "port": port, "error": str(exc)},
        )



def _extract_host(value: str) -> str:
    if "://" in value:
        return urlparse(value).hostname or value
    return value
