import math
from pathlib import Path

import numpy as np
import pytest
from moviepy.editor import AudioClip, ColorClip

from audio_extractor_enhancer.extraction import (
    AudioExtractionError,
    extract_audio,
)


def _create_test_video(path: Path, duration: float = 0.5) -> None:
    """Generate a tiny video clip with an audio track for testing."""

    sample_rate = 44100
    fps = 24

    def tone(t: float) -> float:
        return math.sin(2 * math.pi * 440 * t)

    audio_clip = AudioClip(lambda t: np.array([tone(tt) for tt in np.atleast_1d(t)]), duration=duration, fps=sample_rate)
    video_clip = ColorClip(size=(64, 64), color=(255, 0, 0), duration=duration)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(
        str(path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )
    video_clip.close()
    audio_clip.close()


def test_extract_audio_creates_wav(tmp_path: Path) -> None:
    video_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.wav"

    _create_test_video(video_path)

    extracted_path = extract_audio(video_path, output_path)

    assert extracted_path == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_extract_audio_missing_file(tmp_path: Path) -> None:
    video_path = tmp_path / "missing.mp4"
    output_path = tmp_path / "output.wav"

    with pytest.raises(FileNotFoundError):
        extract_audio(video_path, output_path)


def test_extract_audio_invalid_video(tmp_path: Path) -> None:
    video_path = tmp_path / "invalid.mp4"
    output_path = tmp_path / "output.wav"

    video_path.write_text("not a real video")

    with pytest.raises(AudioExtractionError):
        extract_audio(video_path, output_path)

