# Audio Extractor & Enhancer

![Streamlit demo placeholder](docs/images/gui-demo.gif)

End-to-end toolkit to pull music out of a video file, clean it up, and export a polished soundtrack. The project now includes a command-line workflow and a Streamlit GUI so non-technical users can run the pipeline as well.

## Features
- **Video audio extraction** using MoviePy/FFmpeg utilities with error handling.
- **Source separation** via Spleeter (or compatible engines) to split music and vocals.
- **Audio enhancement** with configurable EQ, gain staging, and noise reduction built on PyDub, librosa, and SciPy.
- **Interactive GUI** powered by Streamlit featuring upload, staged buttons, progress, logging, previews, and downloads.
- **Modular architecture** ready for batch jobs, alternate engines, or future AI enhancement modules.

## Project Structure
```
├── src/
│   └── audio_extractor_enhancer/
│       ├── enhancement.py
│       ├── extraction.py
│       ├── separation.py
│       ├── pipeline.py
│       ├── cli.py
│       └── app_gui.py
├── data/
│   ├── input/
│   └── output/
│       └── gui_sessions/
├── configs/
│   └── default.yaml
├── docs/
│   ├── README.md
│   ├── images/
│   └── waveforms/
├── notebooks/
├── tests/
│   ├── test_enhancement.py
│   ├── test_extraction.py
│   └── test_separation.py
├── requirements.txt
└── pyproject.toml
```

## Installation
1. Install [FFmpeg](https://ffmpeg.org/) and ensure the binaries are on your `PATH`.
2. Create a Python 3.10+ virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the project dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. (Optional) For development tooling:
   ```bash
   pip install -e .[dev]
   ```

## Usage
### CLI
Run the full pipeline from the terminal:
```bash
python -m audio_extractor_enhancer.cli path/to/video.mp4 \
    --output data/output/enhanced_music.wav \
    --work-dir data/output/work \
    --isolate-vocals
```

### Streamlit GUI
```bash
streamlit run src/audio_extractor_enhancer/app_gui.py
```
The interface lets you upload a video, run each phase step-by-step, adjust enhancement sliders, preview audio, and download the final track. Upload screenshots or GIFs to `docs/images/` for the GitHub README badge above.

## Pipeline Overview
1. **Extract Audio** – loads the video, converts the soundtrack to WAV.
2. **Isolate Music** – leverages Spleeter/Demucs to produce `music.wav` and `vocals.wav` stems.
3. **Enhance Audio** – applies pre-emphasis, parametric EQ, noise reduction, and gain according to the chosen profile or GUI sliders.
4. **Export** – writes the mastered track to the output path and surfaces previews/downloads in the UI.

## Testing
Tests rely on optional media libraries; install requirements first, then run:
```bash
python3 -m pytest
```
Pytest will automatically skip suites when dependencies are missing, but running them verifies extraction, separation, and enhancement flows.

## Documentation Assets
Place GUI screenshots (`.png`, `.gif`) in `docs/images/` and waveform comparisons in `docs/waveforms/`. Reference them from the README or other docs prior to publishing on GitHub.

## Roadmap
- [x] Phase 1 – Scaffolding
- [x] Phase 2 – Audio Extraction
- [x] Phase 3 – Source Separation
- [x] Phase 4 – Enhancement
- [x] Phase 5 – GUI
- [x] Phase 6 – Documentation polish
- [ ] Optional – Advanced AI enhancement modules & batch processing UI

