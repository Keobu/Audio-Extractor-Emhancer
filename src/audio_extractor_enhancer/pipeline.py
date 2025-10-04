"""Core orchestration logic for the audio extraction and enhancement pipeline."""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .enhancement import EnhancementSettings, enhance_music
from .extraction import extract_audio
from .separation import separate_music_and_vocals

LOGGER = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration container for pipeline paths and options."""

    input_path: Path
    work_dir: Path
    output_path: Path
    isolate_vocals: bool = False
    isolate_music: bool = True
    enhancement_profile: Optional[str] = None


class AudioProcessingPipeline:
    """End-to-end pipeline combining extraction, separation, and enhancement."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create working directories so later stages can write intermediate files."""

        self.config.work_dir.mkdir(parents=True, exist_ok=True)
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)

    def extract_audio(self) -> Path:
        """Extract the raw audio track from the configured input video."""

        extracted_path = self.config.work_dir / "extracted_audio.wav"
        LOGGER.debug("Extracting audio from %s to %s", self.config.input_path, extracted_path)
        return extract_audio(self.config.input_path, extracted_path)

    def separate_sources(self, audio_path: Path) -> Path:
        """Separate audio into stems and return the selected output track."""

        separation_dir = self.config.work_dir / "separation"
        music_path, vocals_path = separate_music_and_vocals(audio_path, separation_dir)

        if self.config.isolate_vocals:
            target_vocals = self.config.work_dir / "vocals.wav"
            target_vocals.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vocals_path, target_vocals)

        if not self.config.isolate_music:
            return vocals_path

        target_music = self.config.work_dir / "music.wav"
        shutil.copy2(music_path, target_music)
        return target_music

    def _resolve_enhancement_settings(self) -> EnhancementSettings:
        profile = (self.config.enhancement_profile or "default").lower()

        if profile == "bright":
            return EnhancementSettings(eq_high_gain_db=4.0, eq_mid_gain_db=-1.0, target_gain_db=1.5)
        if profile == "warm":
            return EnhancementSettings(eq_low_gain_db=3.0, eq_high_gain_db=-2.0, noise_reduction=False)
        if profile == "clean":
            return EnhancementSettings(eq_low_gain_db=1.0, eq_mid_gain_db=1.5, eq_high_gain_db=1.0, target_gain_db=0.5)

        if profile not in {"default", ""}:
            LOGGER.warning("Unknown enhancement profile '%s'; using defaults", profile)
        return EnhancementSettings()

    def enhance_audio(self, music_path: Path) -> Path:
        """Apply post-processing filters to the chosen music track."""

        settings = self._resolve_enhancement_settings()
        LOGGER.debug("Enhancing audio %s with profile %s", music_path, self.config.enhancement_profile)
        return enhance_music(music_path, self.config.output_path, settings)

    def run(self) -> Path:
        """Execute the pipeline end-to-end using the configured stages."""

        extracted_audio = self.extract_audio()
        selected_track = self.separate_sources(extracted_audio)
        return self.enhance_audio(selected_track)


__all__ = ["PipelineConfig", "AudioProcessingPipeline"]

