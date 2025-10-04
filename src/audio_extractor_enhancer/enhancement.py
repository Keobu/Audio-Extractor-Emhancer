"""Audio enhancement helpers to clean and boost separated music tracks."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np

try:  # pragma: no cover - availability tested via runtime checks
    from pydub import AudioSegment
except ImportError:  # pragma: no cover - handled in logic
    AudioSegment = None  # type: ignore[assignment]

try:  # pragma: no cover - availability tested via runtime checks
    import librosa
except ImportError:  # pragma: no cover - handled in logic
    librosa = None  # type: ignore[assignment]

try:  # pragma: no cover - availability tested via runtime checks
    from scipy import signal
except ImportError:  # pragma: no cover - handled in logic
    signal = None  # type: ignore[assignment]

PathLike = Union[str, Path]
LOGGER = logging.getLogger(__name__)


class AudioEnhancementError(RuntimeError):
    """Raised when an audio enhancement step fails or prerequisites are missing."""


@dataclass(slots=True)
class EnhancementSettings:
    """Tweakable parameters for the enhancement pipeline."""

    eq_low_gain_db: float = 0.0
    eq_mid_gain_db: float = 0.0
    eq_high_gain_db: float = 0.0
    apply_preemphasis: bool = True
    noise_reduction: bool = True
    target_gain_db: float = 0.0


def _require_dependencies() -> None:
    if AudioSegment is None or librosa is None or signal is None:
        missing = [
            name
            for name, module in (
                ("pydub", AudioSegment),
                ("librosa", librosa),
                ("scipy", signal),
            )
            if module is None
        ]
        raise AudioEnhancementError(
            "Missing dependencies for enhancement: " + ", ".join(missing)
        )


def _load_segment(audio_path: Path) -> AudioSegment:
    try:
        return AudioSegment.from_file(audio_path)
    except FileNotFoundError:
        raise
    except Exception as exc:  # pragma: no cover - external library errors
        raise AudioEnhancementError(
            f"Unable to read audio file '{audio_path}': {exc}"
        ) from exc


def _segment_to_numpy(segment: AudioSegment) -> Tuple[np.ndarray, int, int, int]:
    sample_width = segment.sample_width
    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sample_width)
    if dtype is None:
        raise AudioEnhancementError(
            f"Unsupported sample width: {sample_width * 8} bits"
        )

    channels = segment.channels
    frame_rate = segment.frame_rate

    frame_count = len(segment.get_array_of_samples()) // channels
    samples = np.array(segment.get_array_of_samples(), dtype=dtype)
    samples = samples.reshape((frame_count, channels)).T.astype(np.float32)

    max_val = float(2 ** (8 * sample_width - 1))
    return samples / max_val, channels, frame_rate, sample_width


def _numpy_to_segment(
    samples: np.ndarray,
    channels: int,
    frame_rate: int,
    sample_width: int,
) -> AudioSegment:
    max_val = float(2 ** (8 * sample_width - 1) - 1)
    clipped = np.clip(samples, -1.0, 1.0)

    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sample_width)
    if dtype is None:  # pragma: no cover - guarded earlier
        raise AudioEnhancementError(
            f"Unsupported sample width: {sample_width * 8} bits"
        )

    scaled = (clipped * max_val).astype(dtype)
    interleaved = scaled.T.reshape(-1)

    try:
        segment = AudioSegment(
            interleaved.tobytes(),
            frame_rate=frame_rate,
            sample_width=sample_width,
            channels=channels,
        )
    except Exception as exc:  # pragma: no cover - external library errors
        raise AudioEnhancementError(
            f"Failed to rebuild audio segment: {exc}"
        ) from exc

    return segment


def _apply_equalizer(channel: np.ndarray, sr: int, settings: EnhancementSettings) -> np.ndarray:
    nyquist = sr / 2.0
    eps = 1e-4

    def _norm(freq: float) -> float:
        return max(eps, min(freq / nyquist, 0.99))

    gains = {
        "low": settings.eq_low_gain_db,
        "mid": settings.eq_mid_gain_db,
        "high": settings.eq_high_gain_db,
    }

    low_b, low_a = signal.butter(4, _norm(200.0), btype="low")  # type: ignore[arg-type]
    mid_b, mid_a = signal.butter(4, [_norm(200.0), _norm(2000.0)], btype="band")  # type: ignore[arg-type]
    high_b, high_a = signal.butter(4, _norm(4000.0), btype="high")  # type: ignore[arg-type]

    low = signal.lfilter(low_b, low_a, channel)
    mid = signal.lfilter(mid_b, mid_a, channel)
    high = signal.lfilter(high_b, high_a, channel)

    def _gain(db: float) -> float:
        return 10 ** (db / 20.0)

    return (low * _gain(gains["low"]) + mid * _gain(gains["mid"]) + high * _gain(gains["high"]))


def _apply_noise_reduction(channel: np.ndarray) -> np.ndarray:
    return signal.wiener(channel)


def enhance_music(
    audio_path: PathLike,
    output_path: PathLike,
    settings: Optional[EnhancementSettings] = None,
) -> Path:
    """Enhance a music track with EQ, gentle noise reduction, and gain staging."""

    _require_dependencies()
    settings = settings or EnhancementSettings()

    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    segment = _load_segment(audio_path)
    samples, channels, frame_rate, sample_width = _segment_to_numpy(segment)

    enhanced = np.zeros_like(samples)

    for idx in range(channels):
        channel = samples[idx]

        if settings.apply_preemphasis:
            channel = librosa.effects.preemphasis(channel)  # type: ignore[union-attr]

        channel = _apply_equalizer(channel, frame_rate, settings)

        if settings.noise_reduction:
            channel = _apply_noise_reduction(channel)

        enhanced[idx] = channel

    if abs(settings.target_gain_db) > 1e-6:
        enhanced *= 10 ** (settings.target_gain_db / 20.0)

    enhanced_segment = _numpy_to_segment(enhanced, channels, frame_rate, sample_width)

    fmt = output_path.suffix.lstrip(".").lower() or "wav"
    try:
        enhanced_segment.export(str(output_path), format=fmt)
    except Exception as exc:  # pragma: no cover - external library errors
        raise AudioEnhancementError(
            f"Failed to export enhanced audio to '{output_path}': {exc}"
        ) from exc

    LOGGER.debug("Enhanced audio written to %s", output_path)
    return output_path


__all__ = ["AudioEnhancementError", "EnhancementSettings", "enhance_music"]

