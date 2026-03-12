import sqlite3
from scanner.models import MediaFile


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            size_bytes INTEGER,
            mtime REAL,
            duration_secs REAL,
            width INTEGER,
            height INTEGER,
            fps REAL,
            video_codec TEXT,
            video_bitrate_kbps INTEGER,
            overall_bitrate_kbps INTEGER,
            hdr TEXT,
            container TEXT,
            scanned_at TEXT
        );

        CREATE TABLE IF NOT EXISTS audio_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id INTEGER REFERENCES media(id) ON DELETE CASCADE,
            track_index INTEGER,
            codec TEXT,
            channels INTEGER,
            language TEXT,
            is_default INTEGER
        );

        CREATE TABLE IF NOT EXISTS subtitle_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id INTEGER REFERENCES media(id) ON DELETE CASCADE,
            track_index INTEGER,
            codec TEXT,
            language TEXT,
            forced INTEGER,
            is_default INTEGER
        );
    """)
    conn.commit()


def upsert_media(conn: sqlite3.Connection, media: MediaFile) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.execute(
        """
        INSERT INTO media
            (path, filename, size_bytes, mtime, duration_secs, width, height,
             fps, video_codec, video_bitrate_kbps, overall_bitrate_kbps,
             hdr, container, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            filename=excluded.filename,
            size_bytes=excluded.size_bytes,
            mtime=excluded.mtime,
            duration_secs=excluded.duration_secs,
            width=excluded.width,
            height=excluded.height,
            fps=excluded.fps,
            video_codec=excluded.video_codec,
            video_bitrate_kbps=excluded.video_bitrate_kbps,
            overall_bitrate_kbps=excluded.overall_bitrate_kbps,
            hdr=excluded.hdr,
            container=excluded.container,
            scanned_at=excluded.scanned_at
        """,
        (
            media.path, media.filename, media.size_bytes, media.mtime,
            media.duration_secs, media.width, media.height, media.fps,
            media.video_codec, media.video_bitrate_kbps, media.overall_bitrate_kbps,
            media.hdr, media.container, media.scanned_at,
        ),
    )
    media_id = conn.execute("SELECT id FROM media WHERE path = ?", (media.path,)).fetchone()[0]

    conn.execute("DELETE FROM audio_tracks WHERE media_id = ?", (media_id,))
    conn.execute("DELETE FROM subtitle_tracks WHERE media_id = ?", (media_id,))

    for t in media.audio_tracks:
        conn.execute(
            "INSERT INTO audio_tracks (media_id, track_index, codec, channels, language, is_default) VALUES (?,?,?,?,?,?)",
            (media_id, t.track_index, t.codec, t.channels, t.language, int(t.is_default)),
        )

    for t in media.subtitle_tracks:
        conn.execute(
            "INSERT INTO subtitle_tracks (media_id, track_index, codec, language, forced, is_default) VALUES (?,?,?,?,?,?)",
            (media_id, t.track_index, t.codec, t.language, int(t.forced), int(t.is_default)),
        )

    conn.commit()


def get_mtimes(conn: sqlite3.Connection) -> dict[str, float]:
    rows = conn.execute("SELECT path, mtime FROM media").fetchall()
    return {row[0]: row[1] for row in rows}


def remove_deleted(conn: sqlite3.Connection, existing_paths: set[str]) -> None:
    conn.execute("PRAGMA foreign_keys = ON")
    db_paths = {row[0] for row in conn.execute("SELECT path FROM media").fetchall()}
    to_delete = db_paths - existing_paths
    for path in to_delete:
        conn.execute("DELETE FROM media WHERE path = ?", (path,))
    conn.commit()
