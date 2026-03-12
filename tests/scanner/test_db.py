import sqlite3
import pytest
from datetime import datetime, timezone
from scanner.db import init_db, upsert_media, remove_deleted, get_mtimes
from scanner.models import MediaFile, AudioTrack, SubtitleTrack


def make_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def sample_media(path: str = "/media/test.mkv", mtime: float = 1000.0) -> MediaFile:
    return MediaFile(
        path=path,
        filename="test.mkv",
        size_bytes=1000000,
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
        audio_tracks=[
            AudioTrack(track_index=0, codec="truehd", channels=8, language="eng", is_default=True)
        ],
        subtitle_tracks=[
            SubtitleTrack(track_index=1, codec="subrip", language="eng", forced=False, is_default=True)
        ],
    )


def test_upsert_creates_row():
    conn = make_db()
    media = sample_media()
    upsert_media(conn, media)

    row = conn.execute("SELECT * FROM media WHERE path = ?", (media.path,)).fetchone()
    assert row is not None
    assert row["filename"] == "test.mkv"
    assert row["video_codec"] == "HEVC"
    assert row["hdr"] == "HDR10"
    assert row["width"] == 1920

    audio = conn.execute("SELECT * FROM audio_tracks").fetchall()
    assert len(audio) == 1
    assert audio[0]["language"] == "eng"

    subs = conn.execute("SELECT * FROM subtitle_tracks").fetchall()
    assert len(subs) == 1
    assert subs[0]["language"] == "eng"


def test_upsert_updates_on_mtime_change():
    conn = make_db()
    media = sample_media(mtime=1000.0)
    upsert_media(conn, media)

    updated = sample_media(mtime=2000.0)
    updated.video_codec = "H264"
    upsert_media(conn, updated)

    rows = conn.execute("SELECT * FROM media").fetchall()
    assert len(rows) == 1
    assert rows[0]["video_codec"] == "H264"
    assert rows[0]["mtime"] == 2000.0


def test_upsert_replaces_tracks_on_update():
    conn = make_db()
    media = sample_media(mtime=1000.0)
    upsert_media(conn, media)

    updated = sample_media(mtime=2000.0)
    updated.audio_tracks = [
        AudioTrack(track_index=0, codec="aac", channels=2, language="fra", is_default=True),
        AudioTrack(track_index=1, codec="ac3", channels=6, language="deu", is_default=False),
    ]
    upsert_media(conn, updated)

    audio = conn.execute("SELECT * FROM audio_tracks").fetchall()
    assert len(audio) == 2
    langs = [r["language"] for r in audio]
    assert "fra" in langs
    assert "deu" in langs


def test_get_mtimes_returns_path_mtime_map():
    conn = make_db()
    upsert_media(conn, sample_media("/a/one.mkv", mtime=111.0))
    upsert_media(conn, sample_media("/a/two.mkv", mtime=222.0))

    mtimes = get_mtimes(conn)
    assert mtimes == {"/a/one.mkv": 111.0, "/a/two.mkv": 222.0}


def test_remove_deleted_removes_missing_paths():
    conn = make_db()
    upsert_media(conn, sample_media("/a/keep.mkv"))
    upsert_media(conn, sample_media("/a/gone.mkv"))

    remove_deleted(conn, existing_paths={"/a/keep.mkv"})

    rows = conn.execute("SELECT path FROM media").fetchall()
    assert len(rows) == 1
    assert rows[0]["path"] == "/a/keep.mkv"


def test_remove_deleted_cascades_tracks():
    conn = make_db()
    upsert_media(conn, sample_media("/a/gone.mkv"))
    media_id = conn.execute("SELECT id FROM media WHERE path = ?", ("/a/gone.mkv",)).fetchone()["id"]

    audio_before = conn.execute("SELECT * FROM audio_tracks WHERE media_id = ?", (media_id,)).fetchall()
    assert len(audio_before) == 1

    remove_deleted(conn, existing_paths=set())

    audio_after = conn.execute("SELECT * FROM audio_tracks WHERE media_id = ?", (media_id,)).fetchall()
    assert len(audio_after) == 0
