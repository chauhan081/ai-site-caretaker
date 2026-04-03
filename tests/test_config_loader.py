from pathlib import Path
import unittest

from src.config_loader import load_targets


class ConfigLoaderTests(unittest.TestCase):
    def test_load_targets_reads_json(self) -> None:
        temp_dir = Path(__file__).resolve().parent
        cfg = temp_dir / 'targets.temp.json'
        cfg.write_text('{"targets": [{"name": "demo", "url": "https://example.com", "host": "example.com", "checks": ["site", "server"], "server_ports": [80, 443], "log_paths": ["app.log"]}]}', encoding='utf-8')
        try:
            targets = load_targets(cfg)
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0].name, 'demo')
            self.assertEqual(targets[0].host, 'example.com')
            self.assertEqual(targets[0].checks, ['site', 'server'])
            self.assertEqual(targets[0].server_ports, [80, 443])
            self.assertEqual(targets[0].log_paths, ['app.log'])
        finally:
            if cfg.exists():
                cfg.unlink()


if __name__ == '__main__':
    unittest.main()
