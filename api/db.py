import sqlite3
from typing import Optional

_RESOLUTION_BUCKETS = {
    "480p":  (0, 479),
    "720p":  (480, 719),
    "1080p": (720, 1079),
    "1440p": (1080, 1439),
    "2160p": (1440, 9999),
}

_SORTABLE_COLUMNS = {
    "filename", "size_bytes", "duration_secs", "width", "height",
    "fps", "video_codec", "hdr", "container", "scanned_at",
}


def _resolution_clause(resolution: str) -> tuple[str, list]:
    bucket = _RESOLUTION_BUCKETS.get(resolution)
    if bucket is None:
        return ("1=0", [])
    lo, hi = bucket
    return ("m.height >= ? AND m.height <= ?", [lo + 1, hi + 1])


def get_media(
    conn: sqlite3.Connection,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "filename",
    sort_dir: str = "asc",
    resolution: Optional[str] = None,
    codec: Optional[str] = None,
    hdr: Optional[str] = None,
    container: Optional[str] = None,
    audio_lang: Optional[str] = None,
    sub_lang: Optional[str] = None,
) -> tuple[int, list[dict]]:
    if sort_by not in _SORTABLE_COLUMNS:
        sort_by = "filename"
    if sort_dir.lower() not in ("asc", "desc"):
        sort_dir = "asc"

    wheres: list[str] = []
    params: list = []

    if resolution:
        clause, rparams = _resolution_clause(resolution)
        wheres.append(clause)
        params.extend(rparams)

    if codec:
        wheres.append("m.video_codec = ?")
        params.append(codec)

    if hdr:
        wheres.append("m.hdr = ?")
        params.append(hdr)

    if container:
        wheres.append("m.container = ?")
        params.append(container)

    if audio_lang:
        wheres.append("EXISTS (SELECT 1 FROM audio_tracks a WHERE a.media_id = m.id AND a.language = ?)")
        params.append(audio_lang)

    if sub_lang:
        wheres.append("EXISTS (SELECT 1 FROM subtitle_tracks s WHERE s.media_id = m.id AND s.language = ?)")
        params.append(sub_lang)

    where_sql = ("WHERE " + " AND ".join(wheres)) if wheres else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM media m {where_sql}", params
    ).fetchone()[0]

    rows = conn.execute(
        f"""
        SELECT m.*
        FROM media m
        {where_sql}
        ORDER BY m.{sort_by} {sort_dir.upper()}
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    ).fetchall()

    items = []
    for row in rows:
        item = dict(row)
        item["audio_tracks"] = _get_audio_tracks(conn, item["id"])
        item["subtitle_tracks"] = _get_subtitle_tracks(conn, item["id"])
        items.append(item)

    return total, items


def get_media_by_id(conn: sqlite3.Connection, media_id: int) -> Optional[dict]:
    row = conn.execute("SELECT * FROM media WHERE id = ?", (media_id,)).fetchone()
    if row is None:
        return None
    item = dict(row)
    item["audio_tracks"] = _get_audio_tracks(conn, media_id)
    item["subtitle_tracks"] = _get_subtitle_tracks(conn, media_id)
    return item


def _get_audio_tracks(conn: sqlite3.Connection, media_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM audio_tracks WHERE media_id = ? ORDER BY track_index",
        (media_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _get_subtitle_tracks(conn: sqlite3.Connection, media_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM subtitle_tracks WHERE media_id = ? ORDER BY track_index",
        (media_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _height_to_resolution(height: Optional[int]) -> Optional[str]:
    if height is None:
        return None
    for label, (lo, hi) in _RESOLUTION_BUCKETS.items():
        if lo < height <= hi + 1:
            return label
    return None


def get_filters(conn: sqlite3.Connection) -> dict:
    codecs = [r[0] for r in conn.execute(
        "SELECT DISTINCT video_codec FROM media WHERE video_codec IS NOT NULL ORDER BY video_codec"
    ).fetchall()]

    hdr_vals = [r[0] for r in conn.execute(
        "SELECT DISTINCT hdr FROM media WHERE hdr IS NOT NULL ORDER BY hdr"
    ).fetchall()]

    containers = [r[0] for r in conn.execute(
        "SELECT DISTINCT container FROM media WHERE container IS NOT NULL ORDER BY container"
    ).fetchall()]

    audio_langs = [r[0] for r in conn.execute(
        "SELECT DISTINCT language FROM audio_tracks WHERE language IS NOT NULL ORDER BY language"
    ).fetchall()]

    sub_langs = [r[0] for r in conn.execute(
        "SELECT DISTINCT language FROM subtitle_tracks WHERE language IS NOT NULL ORDER BY language"
    ).fetchall()]

    heights = [r[0] for r in conn.execute(
        "SELECT DISTINCT height FROM media WHERE height IS NOT NULL"
    ).fetchall()]
    seen: set[str] = set()
    for h in heights:
        label = _height_to_resolution(h)
        if label:
            seen.add(label)
    ordered = ["480p", "720p", "1080p", "1440p", "2160p"]
    resolutions = [r for r in ordered if r in seen]

    return {
        "resolutions": resolutions,
        "codecs": codecs,
        "hdr": hdr_vals,
        "containers": containers,
        "audio_langs": audio_langs,
        "sub_langs": sub_langs,
    }
