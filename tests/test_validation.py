import unittest

from src.models import NotificationTarget, TargetConfig
from src.validation import validate_target


class ValidationTests(unittest.TestCase):
    def test_validate_target_requires_url_host_or_logs(self) -> None:
        errors = validate_target(TargetConfig(name='demo'))
        self.assertTrue(errors)
        self.assertIn('At least one of url, host, or log_paths must be provided.', errors)

    def test_validate_target_rejects_invalid_checks(self) -> None:
        errors = validate_target(TargetConfig(name='demo', host='example.com', checks=['dns']))
        self.assertIn('Unsupported checks requested: dns.', errors)

    def test_validate_target_requires_log_paths_for_logs_check(self) -> None:
        errors = validate_target(TargetConfig(name='demo', checks=['logs']))
        self.assertIn('The logs check requires at least one log path.', errors)

    def test_validate_target_rejects_invalid_ports(self) -> None:
        errors = validate_target(TargetConfig(name='demo', host='example.com', server_ports=[0, 70000]))
        self.assertIn('Server ports must be between 1 and 65535.', errors)

    def test_validate_target_rejects_invalid_notification_target(self) -> None:
        errors = validate_target(
            TargetConfig(
                name='demo',
                host='example.com',
                notification_targets=[
                    NotificationTarget(name='ops', type='pagerduty', destination='', min_severity='urgent')
                ],
            )
        )
        self.assertIn('Unsupported notification target type for ops: pagerduty.', errors)
        self.assertIn('Notification target ops requires a destination.', errors)
        self.assertIn('Notification target ops has invalid min_severity: urgent.', errors)


if __name__ == '__main__':
    unittest.main()
