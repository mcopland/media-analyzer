def test_get_media_by_id(populated_client, populated_db):
    all_resp = populated_client.get("/api/media")
    first_id = all_resp.json()["items"][0]["id"]

    resp = populated_client.get(f"/api/media/{first_id}")
    assert resp.status_code == 200
    item = resp.json()

    assert item["id"] == first_id
    assert "audio_tracks" in item
    assert "subtitle_tracks" in item
    assert len(item["audio_tracks"]) > 0


def test_get_media_by_id_has_full_path(populated_client, populated_db):
    all_resp = populated_client.get("/api/media")
    first_id = all_resp.json()["items"][0]["id"]

    resp = populated_client.get(f"/api/media/{first_id}")
    item = resp.json()
    assert "path" in item
    assert item["path"].startswith("/m/")


def test_get_media_by_id_audio_track_fields(populated_client, populated_db):
    all_resp = populated_client.get("/api/media")
    first_id = all_resp.json()["items"][0]["id"]

    resp = populated_client.get(f"/api/media/{first_id}")
    track = resp.json()["audio_tracks"][0]
    for field in ("track_index", "codec", "channels", "language", "is_default"):
        assert field in track


def test_get_media_by_id_subtitle_track_fields(populated_client, populated_db):
    all_resp = populated_client.get("/api/media?sub_lang=eng")
    assert all_resp.json()["total"] > 0
    item_id = all_resp.json()["items"][0]["id"]

    resp = populated_client.get(f"/api/media/{item_id}")
    sub = resp.json()["subtitle_tracks"][0]
    for field in ("track_index", "codec", "language", "forced", "is_default"):
        assert field in sub


def test_get_media_by_id_not_found(populated_client):
    resp = populated_client.get("/api/media/99999")
    assert resp.status_code == 404
