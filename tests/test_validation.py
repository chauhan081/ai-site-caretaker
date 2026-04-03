import unittest

from src.models import TargetConfig
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


if __name__ == '__main__':
    unittest.main()
