from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audio_extractor_enhancer.separation import (
    SourceSeparationError,
    separate_music_and_vocals,
)


class _FakeSeparator:
    def __init__(self, *_, **__):
        self.called = False

    def separate_to_file(self, audio, destination, filename_format):  # noqa: D401 - interface mimic
        del filename_format
        self.called = True
        audio = Path(audio)
        destination = Path(destination)
        stems_folder = destination / audio.stem
        stems_folder.mkdir(parents=True, exist_ok=True)
        data, samplerate = sf.read(str(audio))
        sf.write(stems_folder / "accompaniment.wav", data, samplerate)
        sf.write(stems_folder / "vocals.wav", data, samplerate)


@pytest.fixture
def sine_wave(tmp_path: Path) -> Path:
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    data = 0.1 * np.sin(2 * np.pi * 440 * t)
    audio_path = tmp_path / "tone.wav"
    sf.write(audio_path, data, sample_rate)
    return audio_path


def test_separate_music_and_vocals_creates_files(monkeypatch, tmp_path: Path, sine_wave: Path) -> None:
    from audio_extractor_enhancer import separation as separation_module

    monkeypatch.setattr(separation_module, "SpleeterSeparator", _FakeSeparator)

    music_path, vocals_path = separate_music_and_vocals(sine_wave, tmp_path)

    assert music_path.exists()
    assert vocals_path.exists()
    assert music_path.read_bytes() == vocals_path.read_bytes()


def test_separate_music_and_vocals_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.wav"

    with pytest.raises(FileNotFoundError):
        separate_music_and_vocals(missing, tmp_path)


def test_separate_music_and_vocals_short_audio(monkeypatch, tmp_path: Path, sine_wave: Path) -> None:
    # Overwrite with a very short clip
    short_path = tmp_path / "short.wav"
    sf.write(short_path, np.zeros(100), 44100)

    with pytest.raises(SourceSeparationError):
        separate_music_and_vocals(short_path, tmp_path)


def test_separate_music_and_vocals_requires_engine(monkeypatch, tmp_path: Path, sine_wave: Path) -> None:
    from audio_extractor_enhancer import separation as separation_module

    monkeypatch.setattr(separation_module, "SpleeterSeparator", None)

    with pytest.raises(SourceSeparationError):
        separate_music_and_vocals(sine_wave, tmp_path)

