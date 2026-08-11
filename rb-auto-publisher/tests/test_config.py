from pathlib import Path

from publisher.config import load_config


def test_load_config():
    cfg = load_config(Path('configs/redbubble.yaml'))
    assert cfg.base_url.startswith('https://')
    assert 'file_input' in cfg.selectors
