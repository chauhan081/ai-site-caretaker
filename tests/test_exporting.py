import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from src.exporting import export_text, resolve_export_path
from src.main import main


class ExportingTests(unittest.TestCase):
    def test_export_text_writes_supported_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / 'report.txt'
            path = export_text('hello', destination)
            self.assertEqual(path, destination)
            self.assertEqual(destination.read_text(encoding='utf-8'), 'hello\n')

    def test_export_text_rejects_unsupported_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / 'report.md'
            with self.assertRaises(ValueError):
                export_text('hello', destination)

    def test_resolve_export_path_supports_timestamped_output_path(self) -> None:
        path = resolve_export_path(
            command_name='daily-report',
            target_name='Example Site',
            as_json=True,
            output_path='reports/report.json',
            timestamped=True,
            now=datetime(2026, 4, 3, 10, 30, 45),
        )
        self.assertEqual(Path('reports/report-20260403-103045.json'), path)

    def test_resolve_export_path_builds_output_dir_filename(self) -> None:
        path = resolve_export_path(
            command_name='diagnose-target',
            target_name='Example Site',
            as_json=False,
            output_dir='reports',
            timestamped=True,
            alerts_only=True,
            min_severity='high',
            now=datetime(2026, 4, 3, 10, 30, 45),
        )
        self.assertEqual(
            Path('reports/example-site-diagnose-target-alerts-min-high-20260403-103045.txt'),
            path,
        )

    def test_resolve_export_path_rejects_output_and_output_dir_together(self) -> None:
        with self.assertRaises(ValueError):
            resolve_export_path(
                command_name='daily-report',
                target_name='example-site',
                as_json=True,
                output_path='reports/report.json',
                output_dir='reports',
            )

    def test_main_rejects_output_and_output_dir_together(self) -> None:
        with self.assertRaises(SystemExit) as error:
            main(['daily-report', 'demo', '--output', 'report.json', '--output-dir', 'reports'])
        self.assertEqual(error.exception.code, 2)

    def test_daily_report_can_export_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(__file__).resolve().parent.parent
            config_path = repo_root / 'config' / 'targets.json'
            backup = config_path.read_text(encoding='utf-8') if config_path.exists() else None
            log_path = Path(temp_dir) / 'app.log'
            log_path.write_text('INFO ok\n', encoding='utf-8')
            output_path = Path(temp_dir) / 'exports' / 'daily-report.json'
            config_path.write_text(
                json.dumps(
                    {
                        'targets': [
                            {
                                'name': 'logs-only',
                                'checks': ['logs'],
                                'log_paths': [str(log_path)],
                            }
                        ]
                    }
                ),
                encoding='utf-8',
            )
            stdout = io.StringIO()
            try:
                with redirect_stdout(stdout):
                    exit_code = main(['daily-report', 'logs-only', '--json', '--output', str(output_path)])
            finally:
                if backup is None:
                    config_path.unlink(missing_ok=True)
                else:
                    config_path.write_text(backup, encoding='utf-8')

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            payload = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(payload['overall_severity'], 'info')
            self.assertEqual(payload['results'][0]['name'], f'read-logs:{log_path}')
            self.assertIn('Exported report to', stdout.getvalue())

    def test_daily_report_can_export_to_output_dir_with_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(__file__).resolve().parent.parent
            config_path = repo_root / 'config' / 'targets.json'
            backup = config_path.read_text(encoding='utf-8') if config_path.exists() else None
            log_path = Path(temp_dir) / 'app.log'
            log_path.write_text('INFO ok\n', encoding='utf-8')
            output_dir = Path(temp_dir) / 'scheduled-exports'
            config_path.write_text(
                json.dumps(
                    {
                        'targets': [
                            {
                                'name': 'logs-only',
                                'checks': ['logs'],
                                'log_paths': [str(log_path)],
                            }
                        ]
                    }
                ),
                encoding='utf-8',
            )
            stdout = io.StringIO()
            try:
                with redirect_stdout(stdout):
                    exit_code = main(['daily-report', 'logs-only', '--json', '--output-dir', str(output_dir), '--timestamped'])
            finally:
                if backup is None:
                    config_path.unlink(missing_ok=True)
                else:
                    config_path.write_text(backup, encoding='utf-8')

            self.assertEqual(exit_code, 0)
            exported_files = list(output_dir.glob('logs-only-daily-report-*.json'))
            self.assertEqual(len(exported_files), 1)
            payload = json.loads(exported_files[0].read_text(encoding='utf-8'))
            self.assertEqual(payload['results'][0]['name'], f'read-logs:{log_path}')
            self.assertIn(str(exported_files[0]), stdout.getvalue())

    def test_diagnose_target_can_export_alert_filtered_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(__file__).resolve().parent.parent
            config_path = repo_root / 'config' / 'targets.json'
            backup = config_path.read_text(encoding='utf-8') if config_path.exists() else None
            log_path = Path(temp_dir) / 'missing-app.log'
            output_path = Path(temp_dir) / 'exports' / 'diagnosis-alerts.json'
            config_path.write_text(
                json.dumps(
                    {
                        'targets': [
                            {
                                'name': 'alerts-demo',
                                'checks': ['logs'],
                                'log_paths': [str(log_path)],
                            }
                        ]
                    }
                ),
                encoding='utf-8',
            )
            stdout = io.StringIO()
            try:
                with redirect_stdout(stdout):
                    exit_code = main([
                        'diagnose-target',
                        'alerts-demo',
                        '--json',
                        '--alerts-only',
                        '--min-severity',
                        'medium',
                        '--output',
                        str(output_path),
                    ])
            finally:
                if backup is None:
                    config_path.unlink(missing_ok=True)
                else:
                    config_path.write_text(backup, encoding='utf-8')

            self.assertEqual(exit_code, 1)
            payload = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(payload['overall_severity'], 'medium')
            self.assertEqual(len(payload['results']), 1)
            self.assertTrue(payload['results'][0]['name'].startswith('read-logs:'))
            self.assertEqual(payload['diagnosis']['failed_checks'], [f'read-logs:{log_path}'])
            self.assertIn('Exported report to', stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
