import tomllib
from dataclasses import dataclass


@dataclass
class ScannerConfig:
    paths: list[str]
    extensions: list[str]
    db_path: str


@dataclass
class ApiConfig:
    host: str
    port: int


@dataclass
class AppConfig:
    scanner: ScannerConfig
    api: ApiConfig


def load_config(path: str) -> AppConfig:
    with open(path, "rb") as f:
        data = tomllib.load(f)

    scanner_data = data["scanner"]
    api_data = data["api"]

    return AppConfig(
        scanner=ScannerConfig(
            paths=scanner_data["paths"],
            extensions=scanner_data["extensions"],
            db_path=scanner_data["db_path"],
        ),
        api=ApiConfig(
            host=api_data["host"],
            port=api_data["port"],
        ),
    )
