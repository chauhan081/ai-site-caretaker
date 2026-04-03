from __future__ import annotations

import argparse
from pathlib import Path

from .alerts import VALID_ALERT_SEVERITIES, filter_results
from .checks import check_server, check_site, check_ssl
from .config_loader import EXAMPLE_CONFIG_PATH, load_targets
from .diagnostics import build_diagnosis
from .exporting import export_text
from .logs import read_logs
from .output import render_diagnosis, render_result, serialize_diagnosis
from .report_format import render_report_summary, serialize_report_summary
from .reporting import build_daily_report
from .validation import validate_target


PROJECT_ROOT = Path(__file__).resolve().parent.parent



def _add_alert_filter_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--alerts-only',
        action='store_true',
        help='Only include failed checks in the rendered aggregate output',
    )
    parser.add_argument(
        '--min-severity',
        choices=VALID_ALERT_SEVERITIES,
        help='Only include checks at or above the selected severity threshold',
    )



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='AI Site Caretaker')
    subparsers = parser.add_subparsers(dest='command', required=True)

    site_parser = subparsers.add_parser('check-site', help='Check website availability over HTTP/HTTPS')
    site_parser.add_argument('url')
    site_parser.add_argument('--json', action='store_true')

    ssl_parser = subparsers.add_parser('check-ssl', help='Check SSL certificate expiry')
    ssl_parser.add_argument('host')
    ssl_parser.add_argument('--port', type=int, default=443)
    ssl_parser.add_argument('--json', action='store_true')

    server_parser = subparsers.add_parser('check-server', help='Check raw TCP connectivity to a host/port')
    server_parser.add_argument('host')
    server_parser.add_argument('--port', type=int, default=80)
    server_parser.add_argument('--json', action='store_true')

    logs_parser = subparsers.add_parser('read-logs', help='Read a log file and summarize the tail')
    logs_parser.add_argument('path')
    logs_parser.add_argument('--lines', type=int, default=50)
    logs_parser.add_argument('--json', action='store_true')

    report_parser = subparsers.add_parser('daily-report', help='Run checks for a configured target')
    report_parser.add_argument('target_name')
    report_parser.add_argument('--json', action='store_true')
    report_parser.add_argument('--output', help='Write the rendered report to a .txt or .json file')
    _add_alert_filter_args(report_parser)

    diagnose_parser = subparsers.add_parser('diagnose-target', help='Run checks and produce a diagnosis for a configured target')
    diagnose_parser.add_argument('target_name')
    diagnose_parser.add_argument('--json', action='store_true')
    diagnose_parser.add_argument('--output', help='Write the rendered diagnosis to a .txt or .json file')
    _add_alert_filter_args(diagnose_parser)

    subparsers.add_parser('about', help='Show project info')
    return parser



def _load_target_or_exit(target_name: str) -> tuple[object | None, int | None]:
    targets = {target.name: target for target in load_targets()}
    target = targets.get(target_name)
    if target is None:
        print(f'Target not found: {target_name}')
        print(f'Create config/targets.json using {EXAMPLE_CONFIG_PATH.name} as a template.')
        return None, 1
    errors = validate_target(target)
    if errors:
        print(f'Target validation failed: {target_name}')
        for error in errors:
            print(f'- {error}')
        return None, 1
    return target, None



def _emit_output(content: str, output_path: str | None = None) -> None:
    print(content)
    if output_path:
        export_text(content, output_path)
        print(f'Exported report to {output_path}')



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'about':
        print('AI Site Caretaker')
        print(f'Project root: {PROJECT_ROOT}')
        print('Available commands: check-site, check-ssl, check-server, read-logs, daily-report, diagnose-target')
        print(f'Example target config: {EXAMPLE_CONFIG_PATH}')
        return 0

    if args.command == 'check-site':
        result = check_site(args.url)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == 'check-ssl':
        result = check_ssl(args.host, port=args.port)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == 'check-server':
        result = check_server(args.host, port=args.port)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == 'read-logs':
        result = read_logs(args.path, lines=args.lines)
        print(render_result(result, as_json=args.json))
        return 0 if result.ok else 1

    if args.command == 'daily-report':
        target, exit_code = _load_target_or_exit(args.target_name)
        if exit_code is not None:
            return exit_code
        results = build_daily_report(target)
        filtered_results = filter_results(
            results,
            alerts_only=args.alerts_only,
            min_severity=args.min_severity,
        )
        if args.json:
            content = render_report_summary(filtered_results, as_json=True)
        else:
            blocks = [render_report_summary(filtered_results)]
            for result in filtered_results:
                blocks.append(render_result(result))
            content = '\n\n'.join(blocks)
        _emit_output(content, args.output)
        failures = sum(1 for result in filtered_results if not result.ok)
        return 0 if failures == 0 else 1

    if args.command == 'diagnose-target':
        target, exit_code = _load_target_or_exit(args.target_name)
        if exit_code is not None:
            return exit_code
        results = build_daily_report(target)
        filtered_results = filter_results(
            results,
            alerts_only=args.alerts_only,
            min_severity=args.min_severity,
        )
        diagnosis = build_diagnosis(filtered_results)
        if args.json:
            payload = serialize_report_summary(filtered_results)
            payload['diagnosis'] = serialize_diagnosis(diagnosis)
            import json
            content = json.dumps(payload, indent=2)
        else:
            blocks = [render_report_summary(filtered_results)]
            blocks.extend(render_result(result) for result in filtered_results)
            blocks.append(render_diagnosis(diagnosis))
            content = '\n\n'.join(blocks)
        _emit_output(content, args.output)
        return 0 if diagnosis.healthy else 1

    parser.error(f'Unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
