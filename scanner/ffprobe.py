import json
import os
import subprocess
from datetime import datetime, timezone
from typing import Optional

from scanner.models import AudioTrack, MediaFile, SubtitleTrack

_CODEC_NAME_MAP = {
    "hevc": "HEVC",
    "h264": "H264",
    "av1": "AV1",
    "vp9": "VP9",
    "mpeg2video": "MPEG2",
    "mpeg4": "MPEG4",
}

_CONTAINER_MAP = {
    "matroska,webm": "mkv",
    "mov,mp4,m4a,3gp,3g2,mj2": "mp4",
    "avi": "avi",
    "mpegts": "ts",
}


def run_ffprobe(path: str) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def detect_hdr(video_stream: dict) -> Optional[str]:
    side_data = video_stream.get("side_data_list", [])
    for entry in side_data:
        if "DOVI" in entry.get("side_data_type", ""):
            return "DV"

    transfer = video_stream.get("color_transfer", "")
    primaries = video_stream.get("color_primaries", "")

    if transfer == "smpte2084" and "bt2020" in primaries:
        return "HDR10"
    if transfer == "arib-std-b67":
        return "HLG"
    if "bt2020" in primaries:
        return None

    if transfer and transfer not in ("", "unknown"):
        return "SDR"
    return None


def _parse_fps(r_frame_rate: str) -> Optional[float]:
    try:
        num, den = r_frame_rate.split("/")
        return round(int(num) / int(den), 3)
    except Exception:
        return None


def _container_from_format(format_name: str) -> Optional[str]:
    return _CONTAINER_MAP.get(format_name)


def _int_or_none(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_streams(path: str, data: dict) -> MediaFile:
    streams = data.get("streams", [])
    fmt = data.get("format", {})

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    sub_streams = [s for s in streams if s.get("codec_type") == "subtitle"]

    width = height = fps = video_codec = video_bitrate_kbps = hdr = None
    if video_stream:
        width = _int_or_none(video_stream.get("width"))
        height = _int_or_none(video_stream.get("height"))
        fps = _parse_fps(video_stream.get("r_frame_rate", ""))
        raw_codec = video_stream.get("codec_name", "")
        video_codec = _CODEC_NAME_MAP.get(raw_codec, raw_codec.upper() if raw_codec else None)
        br = _int_or_none(video_stream.get("bit_rate"))
        video_bitrate_kbps = br // 1000 if br is not None else None
        hdr = detect_hdr(video_stream)

    overall_br = _int_or_none(fmt.get("bit_rate"))
    overall_bitrate_kbps = overall_br // 1000 if overall_br is not None else None

    format_name = fmt.get("format_name", "")
    container = _container_from_format(format_name)
    if container is None and path:
        ext = os.path.splitext(path)[1].lstrip(".")
        container = ext or None

    audio_tracks = []
    for i, s in enumerate(audio_streams):
        disp = s.get("disposition", {})
        audio_tracks.append(AudioTrack(
            track_index=s.get("index", i),
            codec=s.get("codec_name"),
            channels=_int_or_none(s.get("channels")),
            language=s.get("tags", {}).get("language"),
            is_default=bool(disp.get("default", 0)),
        ))

    subtitle_tracks = []
    for i, s in enumerate(sub_streams):
        disp = s.get("disposition", {})
        subtitle_tracks.append(SubtitleTrack(
            track_index=s.get("index", i),
            codec=s.get("codec_name"),
            language=s.get("tags", {}).get("language"),
            forced=bool(disp.get("forced", 0)),
            is_default=bool(disp.get("default", 0)),
        ))

    size = _int_or_none(fmt.get("size"))
    duration = _float_or_none(fmt.get("duration"))

    return MediaFile(
        path=path,
        filename=os.path.basename(path),
        size_bytes=size,
        mtime=None,
        duration_secs=duration,
        width=width,
        height=height,
        fps=fps,
        video_codec=video_codec,
        video_bitrate_kbps=video_bitrate_kbps,
        overall_bitrate_kbps=overall_bitrate_kbps,
        hdr=hdr,
        container=container,
        scanned_at=datetime.now(timezone.utc).isoformat(),
        audio_tracks=audio_tracks,
        subtitle_tracks=subtitle_tracks,
    )
