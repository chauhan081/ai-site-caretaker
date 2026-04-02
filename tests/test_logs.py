from pathlib import Path
import unittest

from src.logs import read_logs


class ReadLogsTests(unittest.TestCase):
    def test_read_logs_detects_error_lines(self) -> None:
        temp_dir = Path(__file__).resolve().parent
        log_file = temp_dir / 'sample.log'
        log_file.write_text('ok\nERROR: boom\nall good\n', encoding='utf-8')
        try:
            result = read_logs(str(log_file), lines=10)
            self.assertTrue(result.ok)
            self.assertEqual(result.details['error_like_lines'], 1)
            self.assertIn('ERROR: boom', result.details['preview'])
        finally:
            if log_file.exists():
                log_file.unlink()


if __name__ == '__main__':
    unittest.main()
