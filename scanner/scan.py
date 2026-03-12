import argparse
import os
import sqlite3

from scanner.config import load_config
from scanner.db import get_mtimes, init_db, remove_deleted, upsert_media
from scanner.ffprobe import parse_streams, run_ffprobe
from scanner.config import ScannerConfig


def scan_directory(conn: sqlite3.Connection, cfg: ScannerConfig, force: bool = False) -> None:
    extensions = {ext.lower() for ext in cfg.extensions}
    found_paths: set[str] = set()

    cached_mtimes = get_mtimes(conn)

    for scan_path in cfg.paths:
        for root, _dirs, files in os.walk(scan_path):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in extensions:
                    continue

                filepath = os.path.join(root, filename)
                found_paths.add(filepath)

                try:
                    mtime = os.path.getmtime(filepath)
                except OSError:
                    continue

                if not force and cached_mtimes.get(filepath) == mtime:
                    continue

                try:
                    data = run_ffprobe(filepath)
                    media = parse_streams(filepath, data)
                    media.mtime = mtime
                    upsert_media(conn, media)
                except Exception as exc:
                    print(f"Error scanning {filepath}: {exc}")

    remove_deleted(conn, found_paths)


def main() -> None:
    parser = argparse.ArgumentParser(description="Media file scanner")
    parser.add_argument("--config", default="config.toml", help="Path to config.toml")
    parser.add_argument("--force", action="store_true", help="Re-scan all files ignoring mtime cache")
    args = parser.parse_args()

    cfg = load_config(args.config)
    conn = sqlite3.connect(cfg.scanner.db_path)
    conn.row_factory = sqlite3.Row
    try:
        init_db(conn)
        scan_directory(conn, cfg.scanner, force=args.force)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
