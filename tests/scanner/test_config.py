import pytest
import tempfile
import os
from scanner.config import load_config, ScannerConfig, ApiConfig


def write_toml(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_load_config_valid():
    path = write_toml("""
[scanner]
paths = ["/tmp/media"]
extensions = [".mkv", ".mp4"]
db_path = "media.db"

[api]
host = "127.0.0.1"
port = 8000
""")
    try:
        cfg = load_config(path)
        assert isinstance(cfg.scanner, ScannerConfig)
        assert cfg.scanner.paths == ["/tmp/media"]
        assert cfg.scanner.extensions == [".mkv", ".mp4"]
        assert cfg.scanner.db_path == "media.db"
        assert isinstance(cfg.api, ApiConfig)
        assert cfg.api.host == "127.0.0.1"
        assert cfg.api.port == 8000
    finally:
        os.unlink(path)


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.toml")


def test_load_config_invalid_toml():
    path = write_toml("this is not [ valid toml !!!{")
    try:
        with pytest.raises(Exception):
            load_config(path)
    finally:
        os.unlink(path)


def test_load_config_missing_scanner_section():
    path = write_toml("""
[api]
host = "127.0.0.1"
port = 8000
""")
    try:
        with pytest.raises((KeyError, ValueError)):
            load_config(path)
    finally:
        os.unlink(path)
