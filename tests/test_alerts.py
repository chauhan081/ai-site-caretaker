import unittest

from src.alerts import VALID_ALERT_SEVERITIES, filter_results
from src.models import CheckResult


class AlertsTests(unittest.TestCase):
    def test_alerts_only_filters_out_ok_results(self) -> None:
        results = [
            CheckResult(name='check-server', ok=True, summary='ok', details={}),
            CheckResult(name='check-site', ok=False, summary='HTTP 404', details={'status': 404}),
        ]

        filtered = filter_results(results, alerts_only=True)

        self.assertEqual([result.name for result in filtered], ['check-site'])

    def test_min_severity_filters_inclusively(self) -> None:
        results = [
            CheckResult(name='read-logs:/tmp/app.log', ok=False, summary='2 errors', details={'error_like_lines': 2}),
            CheckResult(name='check-site', ok=False, summary='HTTP 404', details={'status': 404}),
            CheckResult(name='check-site', ok=False, summary='HTTP 500', details={'status': 500}),
        ]

        filtered = filter_results(results, min_severity='high')

        self.assertEqual([result.summary for result in filtered], ['HTTP 404', 'HTTP 500'])

    def test_valid_alert_severities_skip_info(self) -> None:
        self.assertEqual(VALID_ALERT_SEVERITIES, ('low', 'medium', 'high', 'critical'))


if __name__ == '__main__':
    unittest.main()
