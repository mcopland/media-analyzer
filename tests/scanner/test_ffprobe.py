import json
import os
import pytest
from scanner.ffprobe import parse_streams, detect_hdr
from scanner.models import MediaFile, AudioTrack, SubtitleTrack

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURES, name)) as f:
        return json.load(f)


def test_parse_hevc_hdr10():
    data = load_fixture("hevc_hdr10.json")
    media = parse_streams("/media/movies/sample.mkv", data)

    assert isinstance(media, MediaFile)
    assert media.path == "/media/movies/sample.mkv"
    assert media.filename == "sample.mkv"
    assert media.width == 3840
    assert media.height == 2160
    assert media.video_codec == "HEVC"
    assert media.hdr == "HDR10"
    assert media.container == "mkv"
    assert media.duration_secs == pytest.approx(7256.123, rel=1e-4)
    assert media.size_bytes == 15000000000
    assert len(media.audio_tracks) == 1
    assert media.audio_tracks[0].codec == "truehd"
    assert media.audio_tracks[0].channels == 8
    assert media.audio_tracks[0].language == "eng"
    assert media.audio_tracks[0].is_default is True
    assert len(media.subtitle_tracks) == 1
    assert media.subtitle_tracks[0].language == "eng"


def test_parse_h264_sdr():
    data = load_fixture("h264_sdr.json")
    media = parse_streams("/media/movies/sample.mp4", data)

    assert media.video_codec == "H264"
    assert media.hdr == "SDR"
    assert media.container == "mp4"
    assert media.width == 1920
    assert media.height == 1080
    assert abs(media.fps - 29.97) < 0.01
    assert len(media.audio_tracks) == 1
    assert len(media.subtitle_tracks) == 0


def test_parse_multi_audio_subs():
    data = load_fixture("multi_audio_subs.json")
    media = parse_streams("/media/movies/multi.mkv", data)

    assert len(media.audio_tracks) == 3
    langs = [t.language for t in media.audio_tracks]
    assert "eng" in langs
    assert "fra" in langs
    assert "deu" in langs

    assert len(media.subtitle_tracks) == 3
    forced = [t for t in media.subtitle_tracks if t.forced]
    assert len(forced) == 1
    assert forced[0].language == "eng"


def test_detect_hdr_hdr10():
    stream = {
        "color_transfer": "smpte2084",
        "color_primaries": "bt2020",
        "color_space": "bt2020nc",
    }
    assert detect_hdr(stream) == "HDR10"


def test_detect_hdr_hlg():
    stream = {
        "color_transfer": "arib-std-b67",
        "color_primaries": "bt2020",
        "color_space": "bt2020nc",
    }
    assert detect_hdr(stream) == "HLG"


def test_detect_hdr_sdr():
    stream = {
        "color_transfer": "bt709",
        "color_primaries": "bt709",
        "color_space": "bt709",
    }
    assert detect_hdr(stream) == "SDR"


def test_detect_hdr_dv():
    stream = {
        "color_transfer": "bt2020-10",
        "color_primaries": "bt2020",
        "color_space": "bt2020nc",
        "side_data_list": [{"side_data_type": "DOVI configuration record"}],
    }
    assert detect_hdr(stream) == "DV"


def test_parse_missing_optional_fields():
    data = {
        "streams": [
            {
                "index": 0,
                "codec_type": "video",
                "codec_name": "h264",
                "width": 1280,
                "height": 720,
                "r_frame_rate": "25/1",
                "tags": {},
            }
        ],
        "format": {
            "filename": "/media/minimal.mkv",
            "format_name": "matroska,webm",
            "tags": {},
        },
    }
    media = parse_streams("/media/minimal.mkv", data)
    assert media.duration_secs is None
    assert media.size_bytes is None
    assert media.video_bitrate_kbps is None
    assert media.overall_bitrate_kbps is None
    assert media.hdr is None
