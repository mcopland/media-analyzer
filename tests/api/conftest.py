import sqlite3
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from api.main import create_app
from scanner.db import init_db, upsert_media
from scanner.models import AudioTrack, MediaFile, SubtitleTrack


def make_media(
    path: str,
    filename: str,
    width: int = 1920,
    height: int = 1080,
    video_codec: str = "HEVC",
    hdr: str = "SDR",
    container: str = "mkv",
    duration_secs: float = 3600.0,
    audio_langs: list[str] | None = None,
    sub_langs: list[str] | None = None,
) -> MediaFile:
    audio_tracks = [
        AudioTrack(track_index=i, codec="aac", channels=2, language=lang, is_default=(i == 0))
        for i, lang in enumerate(audio_langs or ["eng"])
    ]
    subtitle_tracks = [
        SubtitleTrack(track_index=i, codec="subrip", language=lang, forced=False, is_default=(i == 0))
        for i, lang in enumerate(sub_langs or [])
    ]
    return MediaFile(
        path=path,
        filename=filename,
        size_bytes=1_000_000_000,
        mtime=1000.0,
        duration_secs=duration_secs,
        width=width,
        height=height,
        fps=23.976,
        video_codec=video_codec,
        video_bitrate_kbps=5000,
        overall_bitrate_kbps=6000,
        hdr=hdr,
        container=container,
        scanned_at=datetime.now(timezone.utc).isoformat(),
        audio_tracks=audio_tracks,
        subtitle_tracks=subtitle_tracks,
    )


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def client(db):
    app = create_app(db)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def populated_db(db):
    rows = [
        make_media("/m/a.mkv", "a.mkv", width=3840, height=2160, video_codec="HEVC", hdr="HDR10", container="mkv", audio_langs=["eng"], sub_langs=["eng"]),
        make_media("/m/b.mkv", "b.mkv", width=1920, height=1080, video_codec="H264", hdr="SDR",  container="mkv", audio_langs=["eng", "fra"], sub_langs=["eng"]),
        make_media("/m/c.mp4", "c.mp4", width=1280, height=720,  video_codec="H264", hdr="SDR",  container="mp4", audio_langs=["deu"]),
        make_media("/m/d.mkv", "d.mkv", width=1920, height=1080, video_codec="HEVC", hdr="HLG",  container="mkv", audio_langs=["fra"]),
        make_media("/m/e.mkv", "e.mkv", width=1920, height=1080, video_codec="AV1",  hdr="SDR",  container="mkv", audio_langs=["eng"], sub_langs=["fra"]),
    ]
    for row in rows:
        upsert_media(db, row)
    return db


@pytest.fixture
def populated_client(populated_db):
    app = create_app(populated_db)
    with TestClient(app) as c:
        yield c
