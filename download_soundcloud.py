#!/usr/bin/env python3
"""
Download the best-available audio from a SoundCloud track or playlist.

By default the file is transcoded to MP3 (320 kbps), but you can keep the
original container/bit-rate delivered by SoundCloud with --keep-original.

Examples
--------
# Re-encode to 256 kbps MP3
python sc_best_audio.py --url https://soundcloud.com/artist/track --quality 256

# Save the exact file SoundCloud serves (no re-encoding)
python sc_best_audio.py --url https://soundcloud.com/artist/track --keep-original
"""
import os
import argparse
from typing import List

import yt_dlp

BASE_DIR = os.path.join("downloads", "audio")


def detect_info(url: str) -> dict:
    """Probe the URL (no download) to see if it is a playlist or single track."""
    ydl_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def build_output_template(info: dict):
    """Return the output path template and whether the URL is a playlist."""
    if info.get("_type") == "playlist":
        tmpl = os.path.join(
            BASE_DIR,
            "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s",
        )
        return tmpl, True
    return os.path.join(BASE_DIR, "all/%(title)s.%(ext)s"), False


def download_best_audio(
    url: str,
    quality: str = "320",
    keep_original: bool = False,
):
    info = detect_info(url)
    outtmpl, is_playlist = build_output_template(info)
    os.makedirs(BASE_DIR, exist_ok=True)

    # Build post-processing chain dynamically
    postprocessors: List[dict] = []
    if not keep_original:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        )
    postprocessors.append({"key": "FFmpegMetadata"})

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": not is_playlist,
        "postprocessors": postprocessors,
        "progress_hooks": [download_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def download_hook(d):
    """CLI progress / completion messages."""
    if d["status"] == "finished":
        print(f"\n✅  Audio downloaded: {d['filename']}")
    elif d["status"] == "downloading":
        print(f"\r⬇️  {d['_percent_str']} of {d['info_dict']['title']}...", end="")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SoundCloud best-audio downloader"
    )
    parser.add_argument(
        "--url",
        help="SoundCloud track or playlist URL",
    )
    parser.add_argument(
        "--quality",
        help="MP3 bitrate (ignored with --keep-original)",
        default="320",
    )
    parser.add_argument(
        "--keep-original",
        action="store_true",
        help="Skip re-encoding; save exactly what SoundCloud delivers",
    )
    args = parser.parse_args()

    url = args.url or input(
        "🎧 Enter SoundCloud URL (track or playlist): "
    ).strip()
    download_best_audio(
        url,
        quality=args.quality,
        keep_original=args.keep_original,
    )
