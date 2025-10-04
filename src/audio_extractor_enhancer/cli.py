"""Command line interface scaffold for the Audio Extractor & Enhancer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import AudioProcessingPipeline, PipelineConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audio-extractor-enhancer",
        description="Extract, isolate, and enhance background music from video files.",
    )
    parser.add_argument("video", type=Path, help="Path to the input video file")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/enhanced_music.wav"),
        help="Path for the enhanced music track",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("data/output/work"),
        help="Directory for intermediate files",
    )
    parser.add_argument(
        "--isolate-vocals",
        action="store_true",
        help="Also export an isolated vocal track during separation",
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Disable music isolation (useful for vocals-only mode)",
    )
    parser.add_argument(
        "--enhancement-profile",
        type=str,
        default=None,
        help="Optional enhancement profile name (to be implemented)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = PipelineConfig(
        input_path=args.video,
        work_dir=args.work_dir,
        output_path=args.output,
        isolate_vocals=args.isolate_vocals,
        isolate_music=not args.no_music,
        enhancement_profile=args.enhancement_profile,
    )
    pipeline = AudioProcessingPipeline(config)
    pipeline.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

