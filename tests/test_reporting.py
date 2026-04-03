import tempfile
import unittest
from pathlib import Path

from src.models import TargetConfig
from src.reporting import build_daily_report


class ReportingTests(unittest.TestCase):
    def test_build_daily_report_respects_selected_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / 'app.log'
            log_path.write_text('INFO ok\nERROR boom\n', encoding='utf-8')

            target = TargetConfig(
                name='demo',
                host='127.0.0.1',
                checks=['server', 'logs'],
                server_ports=[65534, 65533],
                log_paths=[str(log_path)],
            )

            results = build_daily_report(target)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, 'check-server:65534')
        self.assertEqual(results[1].name, 'check-server:65533')
        self.assertTrue(results[2].name.startswith('read-logs:'))


if __name__ == '__main__':
    unittest.main()
