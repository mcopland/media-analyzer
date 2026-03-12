def test_get_filters_empty_db(client):
    resp = client.get("/api/filters")
    assert resp.status_code == 200
    data = resp.json()
    assert data["resolutions"] == []
    assert data["codecs"] == []
    assert data["hdr"] == []
    assert data["containers"] == []
    assert data["audio_langs"] == []
    assert data["sub_langs"] == []


def test_get_filters_values_present(populated_client):
    resp = populated_client.get("/api/filters")
    assert resp.status_code == 200
    data = resp.json()

    assert set(data["codecs"]) == {"HEVC", "H264", "AV1"}
    assert set(data["containers"]) == {"mkv", "mp4"}
    assert "HDR10" in data["hdr"]
    assert "HLG" in data["hdr"]
    assert "SDR" in data["hdr"]


def test_get_filters_resolutions(populated_client):
    resp = populated_client.get("/api/filters")
    resolutions = resp.json()["resolutions"]
    assert "2160p" in resolutions
    assert "1080p" in resolutions
    assert "720p" in resolutions


def test_get_filters_audio_langs(populated_client):
    resp = populated_client.get("/api/filters")
    langs = set(resp.json()["audio_langs"])
    assert "eng" in langs
    assert "fra" in langs
    assert "deu" in langs


def test_get_filters_sub_langs(populated_client):
    resp = populated_client.get("/api/filters")
    langs = set(resp.json()["sub_langs"])
    assert "eng" in langs
    assert "fra" in langs


def test_get_filters_no_null_hdr(client, db):
    from scanner.db import upsert_media
    from scanner.models import MediaFile, AudioTrack
    from datetime import datetime, timezone

    media = MediaFile(
        path="/m/nodolby.mkv",
        filename="nodolby.mkv",
        size_bytes=100,
        mtime=1.0,
        duration_secs=100.0,
        width=1920,
        height=1080,
        fps=24.0,
        video_codec="H264",
        video_bitrate_kbps=5000,
        overall_bitrate_kbps=6000,
        hdr=None,
        container="mkv",
        scanned_at=datetime.now(timezone.utc).isoformat(),
        audio_tracks=[AudioTrack(track_index=0, codec="aac", channels=2, language="eng", is_default=True)],
        subtitle_tracks=[],
    )
    upsert_media(db, media)

    resp = client.get("/api/filters")
    hdr_vals = resp.json()["hdr"]
    assert None not in hdr_vals
