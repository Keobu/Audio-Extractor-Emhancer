from pathlib import Path

import pytest

pytest.importorskip("pydub")
pytest.importorskip("librosa")
pytest.importorskip("scipy")

from pydub import AudioSegment
from pydub.generators import Sine

from audio_extractor_enhancer.enhancement import (
    EnhancementSettings,
    enhance_music,
)


@pytest.fixture
def sine_wave_file(tmp_path: Path) -> Path:
    tone = Sine(440).to_audio_segment(duration=1000)
    input_path = tmp_path / "input.wav"
    tone.export(input_path, format="wav")
    return input_path


def test_enhance_music_preserves_duration(tmp_path: Path, sine_wave_file: Path) -> None:
    output_path = tmp_path / "enhanced.wav"

    settings = EnhancementSettings(eq_low_gain_db=2.0, eq_high_gain_db=1.5, target_gain_db=1.0)
    result_path = enhance_music(sine_wave_file, output_path, settings)

    assert result_path == output_path
    original = AudioSegment.from_file(sine_wave_file)
    enhanced = AudioSegment.from_file(output_path)

    assert abs(len(original) - len(enhanced)) <= 5
    assert enhanced.frame_rate == original.frame_rate
    assert enhanced.channels == original.channels


def test_enhance_music_preserves_sample_width(tmp_path: Path, sine_wave_file: Path) -> None:
    output_path = tmp_path / "enhanced.wav"

    settings = EnhancementSettings(target_gain_db=0.0)
    result_path = enhance_music(sine_wave_file, output_path, settings)

    assert result_path == output_path
    original = AudioSegment.from_file(sine_wave_file)
    enhanced = AudioSegment.from_file(output_path)
    assert enhanced.sample_width == original.sample_width

