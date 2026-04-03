import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src.main import main
from src.models import CheckResult, TargetConfig, NotificationTarget


class MainNotificationTests(unittest.TestCase):
    def test_daily_report_notify_text_uses_named_delivery_target(self) -> None:
        target = TargetConfig(
            name='demo',
            host='example.com',
            checks=['server'],
            notification_targets=[
                NotificationTarget(name='ops-email', type='email', destination='ops@example.com', min_severity='high')
            ],
        )
        stdout = io.StringIO()
        with patch('src.main.load_targets', return_value=[target]), patch(
            'src.main.build_daily_report',
            return_value=[CheckResult(name='check-server:80', ok=False, summary='Connection refused', details={'port': 80})],
        ):
            with redirect_stdout(stdout):
                exit_code = main(['daily-report', 'demo', '--notify-format', 'text', '--notify-target', 'ops-email'])

        self.assertEqual(exit_code, 1)
        rendered = stdout.getvalue()
        self.assertIn('Delivery target: ops-email (email -> ops@example.com)', rendered)
        self.assertIn('check-server:80', rendered)

    def test_diagnose_target_notify_json_exports_structured_payload(self) -> None:
        target = TargetConfig(name='demo', host='example.com', checks=['server'])
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, patch('src.main.load_targets', return_value=[target]), patch(
            'src.main.build_daily_report',
            return_value=[CheckResult(name='check-server:443', ok=True, summary='TCP ok', details={'port': 443})],
        ):
            output_path = Path(temp_dir) / 'notify.json'
            with redirect_stdout(stdout):
                exit_code = main(['diagnose-target', 'demo', '--notify-format', 'json', '--output', str(output_path)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            payload = json.loads(output_path.read_text(encoding='utf-8'))
            self.assertEqual(payload['source_command'], 'diagnose-target')
            self.assertTrue(payload['healthy'])
            self.assertIn('diagnosis', payload)

    def test_notify_target_must_exist(self) -> None:
        target = TargetConfig(name='demo', host='example.com', checks=['server'])
        stdout = io.StringIO()
        with patch('src.main.load_targets', return_value=[target]), patch(
            'src.main.build_daily_report',
            return_value=[CheckResult(name='check-server:80', ok=True, summary='TCP ok', details={'port': 80})],
        ):
            with redirect_stdout(stdout):
                exit_code = main(['daily-report', 'demo', '--notify-format', 'text', '--notify-target', 'missing'])

        self.assertEqual(exit_code, 1)
        self.assertIn('Notification target not found: missing', stdout.getvalue())

    def test_daily_report_can_deliver_to_file_target(self) -> None:
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'delivered.txt'
            target = TargetConfig(
                name='demo',
                host='example.com',
                checks=['server'],
                notification_targets=[
                    NotificationTarget(name='ops-file', type='file', destination=str(output_path), min_severity='medium')
                ],
            )
            with patch('src.main.load_targets', return_value=[target]), patch(
                'src.main.build_daily_report',
                return_value=[CheckResult(name='check-server:80', ok=False, summary='Connection refused', details={'port': 80})],
            ):
                with redirect_stdout(stdout):
                    exit_code = main(['daily-report', 'demo', '--notify-format', 'text', '--notify-target', 'ops-file', '--deliver'])

            self.assertEqual(exit_code, 1)
            self.assertTrue(output_path.exists())
            self.assertIn('Delivered notification to ops-file', stdout.getvalue())
            self.assertIn('check-server:80', output_path.read_text(encoding='utf-8'))

    def test_daily_report_skips_delivery_when_below_threshold(self) -> None:
        stdout = io.StringIO()
        target = TargetConfig(
            name='demo',
            host='example.com',
            checks=['server'],
            notification_targets=[
                NotificationTarget(name='ops-file', type='file', destination='ignored.txt', min_severity='critical')
            ],
        )
        with patch('src.main.load_targets', return_value=[target]), patch(
            'src.main.build_daily_report',
            return_value=[CheckResult(name='check-server:443', ok=True, summary='TCP ok', details={'port': 443})],
        ):
            with redirect_stdout(stdout):
                exit_code = main(['daily-report', 'demo', '--notify-format', 'text', '--notify-target', 'ops-file', '--deliver'])

        self.assertEqual(exit_code, 0)
        self.assertIn('Delivery skipped for ops-file', stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
