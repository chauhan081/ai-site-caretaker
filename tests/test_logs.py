from pathlib import Path
import unittest

from src.logs import read_logs


class ReadLogsTests(unittest.TestCase):
    def test_read_logs_detects_error_lines_and_groups_patterns(self) -> None:
        temp_dir = Path(__file__).resolve().parent
        log_file = temp_dir / 'sample.log'
        log_file.write_text(
            '\n'.join([
                '2026-04-03T10:00:00 ERROR request 123 failed for user 42',
                '2026-04-03T10:00:01 WARN retrying request 123',
                '2026-04-03T10:00:02 ERROR request 999 failed for user 84',
                '2026-04-03T10:00:03 INFO recovered',
            ]) + '\n',
            encoding='utf-8',
        )
        try:
            result = read_logs(str(log_file), lines=10)
            self.assertFalse(result.ok)
            self.assertEqual(result.details['error_like_lines'], 2)
            self.assertEqual(result.details['warning_like_lines'], 1)
            self.assertEqual(result.details['severity_counts']['error'], 2)
            self.assertIn('top recurring pattern', result.summary)
            self.assertEqual(result.details['recurring_patterns'][0]['count'], 2)
            self.assertIn('request <n> failed for user <n>', result.details['recurring_patterns'][0]['pattern'])
            self.assertEqual(result.details['sample_matches'][-1]['severity'], 'info')
            self.assertIn('INFO recovered', result.details['preview'])
        finally:
            if log_file.exists():
                log_file.unlink()


if __name__ == '__main__':
    unittest.main()
