import unittest

from src.checks import check_server


class CheckServerTests(unittest.TestCase):
    def test_check_server_shape(self) -> None:
        result = check_server('127.0.0.1', port=65534)
        self.assertEqual(result.name, 'check-server')
        self.assertIsInstance(result.ok, bool)
        self.assertIn('host', result.details)
        self.assertEqual(result.details['port'], 65534)


if __name__ == '__main__':
    unittest.main()
