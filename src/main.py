from __future__ import annotations

import argparse
from pathlib import Path

from .checks import check_server, check_site, check_ssl
from .output import render_result


PROJECT_ROOT = Path(__file__).resolve().parent.parent



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Site Caretaker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    site_parser = subparsers.add_parser("check-site", help="Check website availability over HTTP/HTTPS")
    site_parser.add_argument("url")
    site_parser.add_argument("--json", action="store_true")

    ssl_parser = subparsers.add_parser("check-ssl", help="Check SSL certificate expiry")
    ssl_parser.add_argument("host")
    ssl_parser.add_argument("--port", type=int, default=443)
    ssl_parser.add_argument("--json", action="store_true")

    server_parser = subparsers.add_parser("check-server", help="Check raw TCP connectivity to a host/port")
    server_parser.add_argument("host")
    server_parser.add_argument("--port", type=int, default=80)
    server_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("about", help="Show project info")
    return parser



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "about":
        print("AI Site Caretaker")
        print(f"Project root: {PROJECT_ROOT}")
        print("Available commands: check-site, check-ssl, check-server")
        return 0

    if args.command == "check-site":
        result = check_site(args.url)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == "check-ssl":
        result = check_ssl(args.host, port=args.port)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == "check-server":
        result = check_server(args.host, port=args.port)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
