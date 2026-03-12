import pytest


def test_get_media_empty_db(client):
    resp = client.get("/api/media")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_media_default_pagination(populated_client):
    resp = populated_client.get("/api/media")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_get_media_limit(populated_client):
    resp = populated_client.get("/api/media?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_get_media_offset(populated_client):
    resp1 = populated_client.get("/api/media?limit=2&offset=0")
    resp2 = populated_client.get("/api/media?limit=2&offset=2")
    items1 = resp1.json()["items"]
    items2 = resp2.json()["items"]
    ids1 = {i["id"] for i in items1}
    ids2 = {i["id"] for i in items2}
    assert ids1.isdisjoint(ids2)


def test_get_media_sort_by_filename_asc(populated_client):
    resp = populated_client.get("/api/media?sort_by=filename&sort_dir=asc")
    filenames = [i["filename"] for i in resp.json()["items"]]
    assert filenames == sorted(filenames)


def test_get_media_sort_by_filename_desc(populated_client):
    resp = populated_client.get("/api/media?sort_by=filename&sort_dir=desc")
    filenames = [i["filename"] for i in resp.json()["items"]]
    assert filenames == sorted(filenames, reverse=True)


def test_get_media_sort_by_size(populated_client):
    resp = populated_client.get("/api/media?sort_by=size_bytes&sort_dir=asc")
    assert resp.status_code == 200


def test_get_media_filter_resolution_1080p(populated_client):
    resp = populated_client.get("/api/media?resolution=1080p")
    data = resp.json()
    assert data["total"] == 3
    for item in data["items"]:
        assert item["height"] == 1080


def test_get_media_filter_resolution_4k(populated_client):
    resp = populated_client.get("/api/media?resolution=2160p")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["height"] == 2160


def test_get_media_filter_resolution_720p(populated_client):
    resp = populated_client.get("/api/media?resolution=720p")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["height"] == 720


def test_get_media_filter_codec_hevc(populated_client):
    resp = populated_client.get("/api/media?codec=HEVC")
    data = resp.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["video_codec"] == "HEVC"


def test_get_media_filter_hdr(populated_client):
    resp = populated_client.get("/api/media?hdr=HDR10")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["hdr"] == "HDR10"


def test_get_media_filter_container(populated_client):
    resp = populated_client.get("/api/media?container=mp4")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["container"] == "mp4"


def test_get_media_filter_audio_lang(populated_client):
    resp = populated_client.get("/api/media?audio_lang=fra")
    data = resp.json()
    assert data["total"] == 2
    for item in data["items"]:
        audio_langs = [t["language"] for t in item["audio_tracks"]]
        assert "fra" in audio_langs


def test_get_media_filter_sub_lang(populated_client):
    resp = populated_client.get("/api/media?sub_lang=fra")
    data = resp.json()
    assert data["total"] == 1
    for item in data["items"]:
        sub_langs = [t["language"] for t in item["subtitle_tracks"]]
        assert "fra" in sub_langs


def test_get_media_combined_filters(populated_client):
    resp = populated_client.get("/api/media?codec=H264&resolution=1080p")
    data = resp.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["video_codec"] == "H264"
    assert item["height"] == 1080


def test_get_media_filter_no_results(populated_client):
    resp = populated_client.get("/api/media?codec=VP9")
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_media_items_have_tracks(populated_client):
    resp = populated_client.get("/api/media")
    items = resp.json()["items"]
    for item in items:
        assert "audio_tracks" in item
        assert "subtitle_tracks" in item


def test_get_media_item_fields(populated_client):
    resp = populated_client.get("/api/media?limit=1")
    item = resp.json()["items"][0]
    for field in ("id", "filename", "path", "width", "height", "video_codec", "hdr", "container", "duration_secs"):
        assert field in item
