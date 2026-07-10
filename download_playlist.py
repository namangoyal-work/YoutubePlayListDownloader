#!/usr/bin/env python3
"""Download a YouTube playlist for offline viewing.

Built on yt-dlp. Safe to re-run: already-downloaded videos are skipped
via an archive file, and partially downloaded videos are resumed.

Usage:
    python3 download_playlist.py <playlist-url>
    python3 download_playlist.py <playlist-url> -o ~/Videos/flight -q 720
    python3 download_playlist.py <playlist-url> --audio-only
    python3 download_playlist.py <playlist-url> --subs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yt_dlp

DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "playlists"
DEFAULT_MAX_HEIGHT = 1080
ARCHIVE_FILENAME = ".downloaded.txt"  # tracks finished videos per playlist folder

# Playlist videos are numbered by position so they sort in order;
# single videos (no index) get just the title.
OUTPUT_TEMPLATE = "%(playlist_index&{:03d} - |)s%(title)s.%(ext)s"


def build_format_selector(max_height: int, audio_only: bool) -> str:
    """Return a yt-dlp format string.

    Prefers mp4/m4a streams so the merged file plays everywhere without
    extra codecs, falling back to the best available otherwise.
    """
    if audio_only:
        return "bestaudio[ext=m4a]/bestaudio"
    h = max_height
    return (
        f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]"
        f"/bestvideo[height<={h}]+bestaudio"
        f"/best[height<={h}]/best"
    )


def build_ydl_options(output_dir: Path, args: argparse.Namespace) -> dict:
    """Assemble the yt-dlp option dict from CLI arguments."""
    opts: dict = {
        "format": build_format_selector(args.quality, args.audio_only),
        "outtmpl": str(output_dir / OUTPUT_TEMPLATE),
        "download_archive": str(output_dir / ARCHIVE_FILENAME),
        "ignoreerrors": True,  # skip unavailable/private videos, keep going
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "merge_output_format": None if args.audio_only else "mp4",
        "noplaylist": False,
        "trim_file_name": 180,  # avoid filesystem limits on long titles
    }
    if args.subs:
        opts.update(
            {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": [args.subs_lang],
                "postprocessors": [{"key": "FFmpegEmbedSubtitle"}],
            }
        )
    return opts


def download_playlist(url: str, args: argparse.Namespace) -> int:
    """Download every video in the playlist. Returns a shell exit code."""
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Saving to: {output_dir}")
    with yt_dlp.YoutubeDL(build_ydl_options(output_dir, args)) as ydl:
        error_code = ydl.download([url])

    if error_code == 0:
        print("\nDone. Re-run the same command to pick up anything that failed.")
    else:
        print(
            "\nFinished with some errors — re-run the same command; "
            "completed videos will be skipped automatically.",
            file=sys.stderr,
        )
    return error_code


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a YouTube playlist for offline viewing.",
    )
    parser.add_argument("url", help="playlist URL (or a single video URL)")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=DEFAULT_MAX_HEIGHT,
        metavar="HEIGHT",
        help=f"max video height, e.g. 720 or 1080 (default: {DEFAULT_MAX_HEIGHT})",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="download audio only (m4a), e.g. for lecture audio",
    )
    parser.add_argument(
        "--subs",
        action="store_true",
        help="embed subtitles (auto-generated if no manual ones exist)",
    )
    parser.add_argument(
        "--subs-lang",
        default="en",
        help="subtitle language code used with --subs (default: en)",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    try:
        return download_playlist(args.url, args)
    except KeyboardInterrupt:
        print("\nInterrupted — re-run the same command to resume.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
