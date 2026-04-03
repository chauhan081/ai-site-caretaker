import json
import unittest

from src.main import main
from src.models import CheckResult, DiagnosisReport
from src.output import serialize_diagnosis, serialize_result
from src.report_format import serialize_report_summary


class OutputFormatTests(unittest.TestCase):
    def test_serialize_result_includes_severity(self) -> None:
        payload = serialize_result(CheckResult(name='check-site', ok=False, summary='HTTP 500', details={'status': 500}))
        self.assertEqual(payload['severity'], 'critical')
        self.assertFalse(payload['ok'])

    def test_serialize_report_summary_contains_results(self) -> None:
        payload = serialize_report_summary([
            CheckResult(name='check-server', ok=True, summary='ok', details={'host': 'example.com', 'port': 80}),
        ])
        self.assertIn('overall_severity', payload)
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(payload['results'][0]['name'], 'check-server')

    def test_serialize_diagnosis_shape(self) -> None:
        payload = serialize_diagnosis(DiagnosisReport(healthy=False, summary='1 check needs attention.', overall_severity='high'))
        self.assertIn('overall_severity', payload)
        self.assertFalse(payload['healthy'])


if __name__ == '__main__':
    unittest.main()
