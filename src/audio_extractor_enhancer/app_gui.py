"""Streamlit application for the Audio Extractor & Enhancer project."""

from __future__ import annotations

import io
import uuid
from pathlib import Path
from typing import Optional

import streamlit as st

from .enhancement import EnhancementSettings, enhance_music
from .extraction import AudioExtractionError, extract_audio
from .separation import SourceSeparationError, separate_music_and_vocals

APP_WORKDIR = Path("data/output/gui_sessions")


def _init_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex[:8]
    if "log" not in st.session_state:
        st.session_state.log = []
    if "progress" not in st.session_state:
        st.session_state.progress = 0
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "extracted_path" not in st.session_state:
        st.session_state.extracted_path = None
    if "music_path" not in st.session_state:
        st.session_state.music_path = None
    if "vocals_path" not in st.session_state:
        st.session_state.vocals_path = None
    if "enhanced_path" not in st.session_state:
        st.session_state.enhanced_path = None

    session_dir = APP_WORKDIR / st.session_state.session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    st.session_state.session_dir = session_dir


def _log(message: str) -> None:
    st.session_state.log.append(message)


def _progress(value: int, text: str) -> None:
    st.session_state.progress = max(0, min(100, value))
    st.session_state.progress_text = text


def _reset_session() -> None:
    preserved_session_id = uuid.uuid4().hex[:8]
    st.session_state.clear()
    st.session_state.session_id = preserved_session_id
    _init_session_state()


def _save_uploaded_file(uploaded_file) -> Optional[Path]:
    if uploaded_file is None:
        return None
    destination = st.session_state.session_dir / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    _log(f"Uploaded video saved to {destination}")
    return destination


def _render_sidebar_controls() -> EnhancementSettings:
    with st.sidebar:
        st.header("Enhancement Settings")
        eq_low = st.slider("Low Shelf Gain (dB)", -12.0, 12.0, 0.0, 0.5)
        eq_mid = st.slider("Mid Band Gain (dB)", -12.0, 12.0, 0.0, 0.5)
        eq_high = st.slider("High Shelf Gain (dB)", -12.0, 12.0, 0.0, 0.5)
        preemphasis = st.checkbox("Pre-emphasis", value=True)
        noise_reduction = st.checkbox("Noise Reduction", value=True)
        target_gain = st.slider("Output Gain (dB)", -12.0, 12.0, 0.0, 0.5)

    return EnhancementSettings(
        eq_low_gain_db=eq_low,
        eq_mid_gain_db=eq_mid,
        eq_high_gain_db=eq_high,
        apply_preemphasis=preemphasis,
        noise_reduction=noise_reduction,
        target_gain_db=target_gain,
    )


def _render_log() -> None:
    st.subheader("Processing Log")
    if not st.session_state.log:
        st.info("No actions performed yet.")
    else:
        st.text_area("Log", value="\n".join(st.session_state.log), height=160)


def _render_audio_preview() -> None:
    st.subheader("Audio Preview")
    if st.session_state.enhanced_path and Path(st.session_state.enhanced_path).exists():
        audio_path = Path(st.session_state.enhanced_path)
        st.audio(audio_path.read_bytes(), format="audio/wav")
    elif st.session_state.music_path and Path(st.session_state.music_path).exists():
        audio_path = Path(st.session_state.music_path)
        st.audio(audio_path.read_bytes(), format="audio/wav")
    else:
        st.info("Run the pipeline to preview audio here.")


def _render_download() -> None:
    if st.session_state.enhanced_path and Path(st.session_state.enhanced_path).exists():
        output_path = Path(st.session_state.enhanced_path)
        st.download_button(
            label="Download Enhanced Audio",
            data=output_path.read_bytes(),
            file_name=output_path.name,
            mime="audio/wav",
        )


def _handle_extract() -> None:
    if not st.session_state.video_path:
        st.warning("Upload a video file first.")
        return

    output_path = st.session_state.session_dir / "extracted_audio.wav"
    _log("Starting audio extraction...")
    _progress(20, "Extracting audio")
    try:
        extracted = extract_audio(st.session_state.video_path, output_path)
    except FileNotFoundError:
        st.error("Uploaded video file could not be found on disk.")
        return
    except AudioExtractionError as exc:
        st.error(str(exc))
        return

    st.session_state.extracted_path = extracted
    st.session_state.music_path = None
    st.session_state.vocals_path = None
    st.session_state.enhanced_path = None
    _progress(40, "Audio extracted")
    _log(f"Audio extracted to {extracted}")
    st.success("Audio extraction completed.")


def _handle_separate() -> None:
    if not st.session_state.extracted_path:
        st.warning("Extract audio before running separation.")
        return

    separation_dir = st.session_state.session_dir / "separation"
    _log("Starting source separation...")
    _progress(60, "Separating music and vocals")
    try:
        music_path, vocals_path = separate_music_and_vocals(
            st.session_state.extracted_path,
            separation_dir,
        )
    except (FileNotFoundError, SourceSeparationError) as exc:
        st.error(str(exc))
        return

    st.session_state.music_path = music_path
    st.session_state.vocals_path = vocals_path
    st.session_state.enhanced_path = None
    _progress(75, "Separation complete")
    _log(f"Music saved to {music_path}; vocals saved to {vocals_path}")
    st.success("Source separation completed.")


def _handle_enhance(settings: EnhancementSettings) -> None:
    if not st.session_state.music_path:
        st.warning("Run separation before enhancement.")
        return

    output_path = st.session_state.session_dir / "enhanced_music.wav"
    _log("Starting enhancement...")
    _progress(85, "Enhancing audio")
    try:
        enhanced_path = enhance_music(
            st.session_state.music_path,
            output_path,
            settings,
        )
    except Exception as exc:  # broad catch to surface user-friendly errors
        st.error(str(exc))
        return

    st.session_state.enhanced_path = enhanced_path
    _progress(100, "Enhancement complete")
    _log(f"Enhanced audio available at {enhanced_path}")
    st.success("Enhancement completed.")


def _render_progress_bar() -> None:
    text = st.session_state.get("progress_text", "Idle")
    st.progress(st.session_state.progress, text=text)


def main() -> None:
    st.set_page_config(page_title="Audio Extractor & Enhancer", layout="wide")
    _init_session_state()

    settings = _render_sidebar_controls()

    st.title("Audio Extractor & Enhancer")
    st.caption("Process videos to isolate and enhance background music without touching the terminal.")

    top_col, reset_col = st.columns([4, 1])
    with reset_col:
        if st.button("New Session"):
            _reset_session()
            st.experimental_rerun()

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "mkv", "avi"])
    if uploaded_file is not None:
        st.session_state.video_path = _save_uploaded_file(uploaded_file)

    _render_progress_bar()

    with st.container():
        extract_col, separate_col, enhance_col = st.columns(3)
        with extract_col:
            if st.button("Extract Audio"):
                _handle_extract()
        with separate_col:
            if st.button("Isolate Music"):
                _handle_separate()
        with enhance_col:
            if st.button("Enhance Audio"):
                _handle_enhance(settings)

    if st.session_state.enhanced_path:
        st.write("✅ Enhancement complete. Use the player below to preview your track.")

    _render_audio_preview()
    _render_download()
    _render_log()

    if st.session_state.vocals_path and Path(st.session_state.vocals_path).exists():
        with st.expander("Vocal Track Preview"):
            audio_bytes = Path(st.session_state.vocals_path).read_bytes()
            st.audio(audio_bytes, format="audio/wav")


if __name__ == "__main__":
    main()

