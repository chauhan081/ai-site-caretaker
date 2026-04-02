import unittest

from src.models import TargetConfig
from src.validation import validate_target


class ValidationTests(unittest.TestCase):
    def test_validate_target_requires_url_or_host(self) -> None:
        errors = validate_target(TargetConfig(name='demo'))
        self.assertTrue(errors)
        self.assertIn('At least one of url or host must be provided.', errors)


if __name__ == '__main__':
    unittest.main()
