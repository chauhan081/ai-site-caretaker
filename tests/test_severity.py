import unittest

from src.models import CheckResult
from src.severity import infer_severity, summarize_overall_severity


class SeverityTests(unittest.TestCase):
    def test_infer_severity_for_site_failure(self) -> None:
        result = CheckResult(name='check-site', ok=False, summary='HTTP 500', details={'status': 500})
        self.assertEqual(infer_severity(result), 'critical')

    def test_summarize_overall_severity(self) -> None:
        results = [
            CheckResult(name='check-server', ok=True, summary='ok', details={}),
            CheckResult(name='check-site', ok=False, summary='HTTP 404', details={'status': 404}),
        ]
        self.assertEqual(summarize_overall_severity(results), 'high')


if __name__ == '__main__':
    unittest.main()
