import json
import os
import sqlite3
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from scanner.db import init_db, get_mtimes
from scanner.scan import scan_directory
from scanner.models import MediaFile, AudioTrack, SubtitleTrack
from scanner.config import ScannerConfig
from datetime import datetime, timezone


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def make_media(path: str, mtime: float = 1000.0) -> MediaFile:
    return MediaFile(
        path=path,
        filename=os.path.basename(path),
        size_bytes=500000000,
        mtime=mtime,
        duration_secs=3600.0,
        width=1920,
        height=1080,
        fps=23.976,
        video_codec="HEVC",
        video_bitrate_kbps=5000,
        overall_bitrate_kbps=6000,
        hdr="HDR10",
        container="mkv",
        scanned_at=datetime.now(timezone.utc).isoformat(),
        audio_tracks=[AudioTrack(track_index=0, codec="aac", channels=2, language="eng", is_default=True)],
        subtitle_tracks=[],
    )


def test_scan_inserts_new_files():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        media_file = os.path.join(tmpdir, "movie.mkv")
        open(media_file, "w").close()
        mtime = os.path.getmtime(media_file)

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mkv"], db_path="")
        parsed = make_media(media_file, mtime=mtime)

        with patch("scanner.scan.run_ffprobe", return_value={}), \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)

        rows = conn.execute("SELECT * FROM media").fetchall()
        assert len(rows) == 1
        assert rows[0]["filename"] == "movie.mkv"


def test_scan_skips_unchanged_files():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        media_file = os.path.join(tmpdir, "movie.mkv")
        open(media_file, "w").close()
        mtime = os.path.getmtime(media_file)

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mkv"], db_path="")
        parsed = make_media(media_file, mtime=mtime)

        with patch("scanner.scan.run_ffprobe", return_value={}) as mock_ffprobe, \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)
            first_call_count = mock_ffprobe.call_count

            scan_directory(conn, cfg, force=False)
            assert mock_ffprobe.call_count == first_call_count


def test_scan_rescans_on_mtime_change():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        media_file = os.path.join(tmpdir, "movie.mkv")
        open(media_file, "w").close()
        mtime = os.path.getmtime(media_file)

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mkv"], db_path="")
        parsed = make_media(media_file, mtime=mtime)

        with patch("scanner.scan.run_ffprobe", return_value={}) as mock_ffprobe, \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)
            assert mock_ffprobe.call_count == 1

            newer = make_media(media_file, mtime=mtime + 1)
            with patch("scanner.scan.run_ffprobe", return_value={}) as mock2, \
                 patch("scanner.scan.parse_streams", return_value=newer), \
                 patch("os.path.getmtime", return_value=mtime + 1):
                scan_directory(conn, cfg, force=False)
                assert mock2.call_count == 1


def test_scan_force_rescans_all():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        media_file = os.path.join(tmpdir, "movie.mkv")
        open(media_file, "w").close()
        mtime = os.path.getmtime(media_file)

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mkv"], db_path="")
        parsed = make_media(media_file, mtime=mtime)

        with patch("scanner.scan.run_ffprobe", return_value={}) as mock_ffprobe, \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)
            assert mock_ffprobe.call_count == 1

            scan_directory(conn, cfg, force=True)
            assert mock_ffprobe.call_count == 2


def test_scan_removes_deleted_files():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        media_file = os.path.join(tmpdir, "movie.mkv")
        open(media_file, "w").close()
        mtime = os.path.getmtime(media_file)

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mkv"], db_path="")
        parsed = make_media(media_file, mtime=mtime)

        with patch("scanner.scan.run_ffprobe", return_value={}), \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)

        rows = conn.execute("SELECT * FROM media").fetchall()
        assert len(rows) == 1

        os.remove(media_file)
        with patch("scanner.scan.run_ffprobe", return_value={}), \
             patch("scanner.scan.parse_streams", return_value=parsed):
            scan_directory(conn, cfg, force=False)

        rows = conn.execute("SELECT * FROM media").fetchall()
        assert len(rows) == 0


def test_scan_ignores_wrong_extensions():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "movie.avi"), "w").close()
        open(os.path.join(tmpdir, "movie.mkv"), "w").close()

        cfg = ScannerConfig(paths=[tmpdir], extensions=[".mp4"], db_path="")

        with patch("scanner.scan.run_ffprobe", return_value={}) as mock_ffprobe, \
             patch("scanner.scan.parse_streams", return_value=MagicMock()):
            scan_directory(conn, cfg, force=False)
            assert mock_ffprobe.call_count == 0
