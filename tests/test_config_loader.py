from pathlib import Path
import unittest

from src.config_loader import load_targets


class ConfigLoaderTests(unittest.TestCase):
    def test_load_targets_reads_json(self) -> None:
        temp_dir = Path(__file__).resolve().parent
        cfg = temp_dir / 'targets.temp.json'
        cfg.write_text('{"targets": [{"name": "demo", "url": "https://example.com", "host": "example.com"}]}', encoding='utf-8')
        try:
            targets = load_targets(cfg)
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0].name, 'demo')
            self.assertEqual(targets[0].host, 'example.com')
        finally:
            if cfg.exists():
                cfg.unlink()


if __name__ == '__main__':
    unittest.main()
