from pathlib import Path
import tomllib
import unittest


class PackagingTests(unittest.TestCase):
    def test_pyproject_exposes_console_script(self) -> None:
        pyproject_path = Path(__file__).resolve().parent.parent / 'pyproject.toml'
        data = tomllib.loads(pyproject_path.read_text(encoding='utf-8'))
        self.assertEqual(data['project']['name'], 'ai-site-caretaker')
        self.assertEqual(data['project']['scripts']['ai-site-caretaker'], 'src.main:main')


if __name__ == '__main__':
    unittest.main()
