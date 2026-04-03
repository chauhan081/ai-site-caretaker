import json
import unittest

from src.models import CheckResult, DiagnosisReport, NotificationTarget
from src.notifications import render_notification_json, render_notification_text, resolve_notification_target, serialize_notification


class NotificationTests(unittest.TestCase):
    def test_resolve_notification_target_by_name(self) -> None:
        targets = [
            NotificationTarget(name='ops-email', type='email', destination='ops@example.com'),
            NotificationTarget(name='slack-webhook', type='webhook', destination='https://hooks.slack.test/abc'),
        ]

        target = resolve_notification_target(targets, 'slack-webhook')

        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual(target.destination, 'https://hooks.slack.test/abc')

    def test_serialize_notification_includes_delivery_target_and_diagnosis(self) -> None:
        payload = serialize_notification(
            'demo',
            [CheckResult(name='check-site', ok=False, summary='HTTP 500', details={'status': 500})],
            diagnosis=DiagnosisReport(
                healthy=False,
                summary='1 check needs attention.',
                recommended_actions=['Inspect upstream logs.'],
                overall_severity='critical',
            ),
            delivery_target=NotificationTarget(
                name='ops-email',
                type='email',
                destination='ops@example.com',
                min_severity='high',
            ),
            source_command='diagnose-target',
        )

        self.assertEqual(payload['target'], 'demo')
        self.assertEqual(payload['failure_count'], 1)
        self.assertEqual(payload['delivery_target']['name'], 'ops-email')
        self.assertEqual(payload['diagnosis']['overall_severity'], 'critical')

    def test_render_notification_text_is_compact_and_actionable(self) -> None:
        text = render_notification_text(
            'demo',
            [CheckResult(name='read-logs:/var/log/app.log', ok=False, summary='3 errors found', details={'error_like_lines': 3})],
            diagnosis=DiagnosisReport(
                healthy=False,
                summary='1 check needs attention.',
                recommended_actions=['Review repeating stack traces.', 'Compare against the last deploy.'],
                overall_severity='high',
            ),
            delivery_target=NotificationTarget(name='ops-email', type='email', destination='ops@example.com'),
            source_command='diagnose-target',
        )

        self.assertIn('[ALERT] demo | severity=HIGH | source=diagnose-target', text)
        self.assertIn('Delivery target: ops-email (email -> ops@example.com)', text)
        self.assertIn('Recommended actions:', text)
        self.assertIn('read-logs:/var/log/app.log', text)

    def test_render_notification_json_outputs_valid_json(self) -> None:
        payload = render_notification_json(
            'demo',
            [CheckResult(name='check-server:443', ok=True, summary='TCP ok', details={'port': 443})],
            source_command='daily-report',
        )

        parsed = json.loads(payload)
        self.assertTrue(parsed['healthy'])
        self.assertEqual(parsed['alert_count'], 1)
        self.assertEqual(parsed['results'][0]['name'], 'check-server:443')


if __name__ == '__main__':
    unittest.main()
