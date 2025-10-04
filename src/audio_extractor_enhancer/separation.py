"""Source separation helpers for isolating music and vocals."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Tuple, Union

import soundfile as sf

try:  # pragma: no cover - import availability tested indirectly
    from spleeter.separator import Separator as SpleeterSeparator
except ImportError:  # pragma: no cover - availability handled in logic
    SpleeterSeparator = None  # type: ignore[assignment]

PathLike = Union[str, Path]

LOGGER = logging.getLogger(__name__)


class SourceSeparationError(RuntimeError):
    """Raised when audio source separation cannot be completed."""


def _validate_input_audio(audio_path: Path) -> None:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    info = sf.info(str(audio_path))
    duration = info.frames / float(info.samplerate)
    if duration < 0.2:
        raise SourceSeparationError(
            f"Audio file is too short for separation (duration={duration:.3f}s)."
        )


def _ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _cleanup_spleeter_workspace(stems_dir: Path) -> None:
    if stems_dir.exists():
        shutil.rmtree(stems_dir, ignore_errors=True)


def separate_music_and_vocals(
    audio_path: PathLike,
    output_dir: PathLike,
    engine: str = "spleeter",
) -> Tuple[Path, Path]:
    """Split an input audio track into music and vocal stems.

    Parameters
    ----------
    audio_path: str or Path
        Path to the source audio file (must be readable by ffmpeg/spleeter).
    output_dir: str or Path
        Directory where the separated stems will be saved.
    engine: str
        Separation backend to use. Currently supports ``"spleeter"``.

    Returns
    -------
    (Path, Path)
        Tuple containing paths to ``music.wav`` and ``vocals.wav`` respectively.

    Raises
    ------
    FileNotFoundError
        If ``audio_path`` does not exist.
    SourceSeparationError
        If separation fails or the required engine is unavailable.
    ValueError
        If an unknown engine is requested.
    """

    audio_path = Path(audio_path)
    output_dir = _ensure_output_dir(Path(output_dir))

    _validate_input_audio(audio_path)

    if engine == "spleeter":
        if SpleeterSeparator is None:
            raise SourceSeparationError(
                "Spleeter is not installed. Install 'spleeter' to enable separation."
            )

        try:
            separator = SpleeterSeparator("spleeter:2stems")
        except Exception as exc:  # pragma: no cover - direct dependency failure
            raise SourceSeparationError(f"Failed to initialize Spleeter: {exc}") from exc

        stems_workspace = output_dir / audio_path.stem
        try:
            separator.separate_to_file(
                str(audio_path),
                str(output_dir),
                filename_format="{filename}/{instrument}.wav",
            )
        except Exception as exc:  # pragma: no cover - delegated to spleeter
            raise SourceSeparationError(
                f"Failed to separate audio '{audio_path}': {exc}"
            ) from exc

        accompaniment_path = stems_workspace / "accompaniment.wav"
        vocals_path = stems_workspace / "vocals.wav"

        if not accompaniment_path.exists() or not vocals_path.exists():
            raise SourceSeparationError(
                "Spleeter did not produce the expected stem files."
            )

        music_target = output_dir / "music.wav"
        vocals_target = output_dir / "vocals.wav"

        if music_target.exists():
            music_target.unlink()
        if vocals_target.exists():
            vocals_target.unlink()

        shutil.move(str(accompaniment_path), str(music_target))
        shutil.move(str(vocals_path), str(vocals_target))
        _cleanup_spleeter_workspace(stems_workspace)

        LOGGER.debug("Separated audio saved to %s and %s", music_target, vocals_target)
        return music_target, vocals_target

    raise ValueError(f"Unsupported separation engine: {engine}")


__all__ = ["SourceSeparationError", "separate_music_and_vocals"]

