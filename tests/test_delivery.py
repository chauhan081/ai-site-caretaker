import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.delivery import DeliveryError, deliver_notification, should_deliver
from src.models import CheckResult, NotificationTarget


class _FakeResponse:
    def __init__(self, status: int = 200) -> None:
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def getcode(self) -> int:
        return self.status


class DeliveryTests(unittest.TestCase):
    def test_should_deliver_respects_enabled_and_min_severity(self) -> None:
        results = [CheckResult(name='read-logs:/var/log/app.log', ok=False, summary='1 error found', details={'error_like_lines': 1})]
        self.assertTrue(should_deliver(results, NotificationTarget(name='ops', type='webhook', destination='https://x.test', min_severity='medium')))
        self.assertFalse(should_deliver(results, NotificationTarget(name='ops', type='webhook', destination='https://x.test', min_severity='high')))
        self.assertFalse(should_deliver(results, NotificationTarget(name='ops', type='webhook', destination='https://x.test', enabled=False)))

    def test_deliver_notification_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / 'notify.txt'
            message = deliver_notification(
                'hello world',
                delivery_target=NotificationTarget(name='local-file', type='file', destination=str(destination)),
                as_json=False,
                source_command='daily-report',
                monitored_target='demo',
            )
            self.assertTrue(destination.exists())
            self.assertEqual(destination.read_text(encoding='utf-8'), 'hello world\n')
            self.assertIn('local-file', message)

    def test_deliver_notification_posts_webhook_json_payload(self) -> None:
        captured = {}

        def fake_urlopen(req, timeout=10):
            captured['url'] = req.full_url
            captured['body'] = req.data.decode('utf-8')
            captured['content_type'] = req.headers.get('Content-type') or req.headers.get('Content-Type')
            return _FakeResponse(204)

        with patch('src.delivery.request.urlopen', side_effect=fake_urlopen):
            message = deliver_notification(
                json.dumps({'healthy': False, 'target': 'demo'}),
                delivery_target=NotificationTarget(name='ops-webhook', type='webhook', destination='https://hooks.test/abc'),
                as_json=True,
                source_command='daily-report',
                monitored_target='demo',
            )

        self.assertEqual(captured['url'], 'https://hooks.test/abc')
        self.assertEqual(json.loads(captured['body'])['target'], 'demo')
        self.assertIn('application/json', captured['content_type'])
        self.assertIn('HTTP 204', message)

    def test_deliver_notification_rejects_email_delivery(self) -> None:
        with self.assertRaises(DeliveryError):
            deliver_notification(
                'hello',
                delivery_target=NotificationTarget(name='ops-email', type='email', destination='ops@example.com'),
                as_json=False,
                source_command='daily-report',
                monitored_target='demo',
            )


if __name__ == '__main__':
    unittest.main()
