"""Utilities for extracting audio tracks from video files."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from moviepy.editor import VideoFileClip

PathLike = Union[str, Path]


class AudioExtractionError(ValueError):
    """Raised when an input video cannot be processed for audio extraction."""


def extract_audio(video_path: PathLike, output_path: PathLike) -> Path:
    """Extract the audio stream from ``video_path`` into a WAV file at ``output_path``.

    Parameters
    ----------
    video_path: str or Path
        Input video file that contains an audio track.
    output_path: str or Path
        Target location for the extracted audio file (``.wav`` recommended).

    Returns
    -------
    Path
        Path to the created audio file.

    Raises
    ------
    FileNotFoundError
        If the input video file does not exist.
    AudioExtractionError
        If the video is invalid or does not contain an audio track.
    """

    video_path = Path(video_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with VideoFileClip(str(video_path)) as clip:
            if clip.audio is None:
                raise AudioExtractionError(
                    f"No audio track found in video: {video_path}"
                )
            clip.audio.write_audiofile(
                str(output_path),
                codec="pcm_s16le",
                logger=None,
            )
    except FileNotFoundError:
        raise
    except Exception as exc:  # pragma: no cover - moviepy raises various errors
        raise AudioExtractionError(
            f"Failed to extract audio from video '{video_path}': {exc}"
        ) from exc

    if not output_path.exists():
        raise AudioExtractionError(
            f"Expected audio file was not created at: {output_path}"
        )

    return output_path


__all__ = ["AudioExtractionError", "extract_audio"]

