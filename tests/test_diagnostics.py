import unittest

from src.diagnostics import build_diagnosis
from src.models import CheckResult


class DiagnosticsTests(unittest.TestCase):
    def test_build_diagnosis_for_failure(self) -> None:
        report = build_diagnosis([
            CheckResult(name='check-site', ok=False, summary='failed', details={}),
            CheckResult(name='check-server', ok=True, summary='ok', details={}),
        ])
        self.assertFalse(report.healthy)
        self.assertIn('check-site', report.failed_checks)
        self.assertTrue(report.recommended_actions)


if __name__ == '__main__':
    unittest.main()
