from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AudioTrack:
    track_index: int
    codec: Optional[str]
    channels: Optional[int]
    language: Optional[str]
    is_default: bool


@dataclass
class SubtitleTrack:
    track_index: int
    codec: Optional[str]
    language: Optional[str]
    forced: bool
    is_default: bool


@dataclass
class MediaFile:
    path: str
    filename: str
    size_bytes: Optional[int]
    mtime: Optional[float]
    duration_secs: Optional[float]
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    video_codec: Optional[str]
    video_bitrate_kbps: Optional[int]
    overall_bitrate_kbps: Optional[int]
    hdr: Optional[str]
    container: Optional[str]
    scanned_at: str
    audio_tracks: list[AudioTrack] = field(default_factory=list)
    subtitle_tracks: list[SubtitleTrack] = field(default_factory=list)
