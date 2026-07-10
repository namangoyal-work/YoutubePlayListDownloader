# YouTube Playlist Downloader

Download a YouTube playlist for offline viewing (e.g. studying on a flight).
A thin, maintainable wrapper around [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Requirements

- Python 3.10+
- `pip3 install yt-dlp`
- ffmpeg (`brew install ffmpeg`) — needed to merge video+audio and embed subtitles

## Usage

```bash
python3 download_playlist.py "https://www.youtube.com/playlist?list=PLxxxx"
```

Common options:

```bash
# 720p to save disk space, custom folder
python3 download_playlist.py "<url>" -q 720 -o ~/Videos/flight

# Embed English subtitles (falls back to auto-generated captions)
python3 download_playlist.py "<url>" --subs

# Audio only (m4a), e.g. lecture audio
python3 download_playlist.py "<url>" --audio-only
```

Files are saved as `001 - Title.mp4`, `002 - ...` so they play in playlist order.

## Resumable by design

- **Interrupted?** Re-run the exact same command. Finished videos are recorded
  in `.downloaded.txt` inside the output folder and skipped; partial files resume.
- **Playlist updated later?** Re-run the same command — only new videos download.
- Private/deleted videos in the playlist are skipped instead of aborting the run.

## Maintenance

All behavior lives in `download_playlist.py`:

- Defaults (output dir, quality, filename pattern) are constants at the top.
- Format selection logic is isolated in `build_format_selector()`.
- yt-dlp options are assembled in one place, `build_ydl_options()` — see the
  full option reference in yt-dlp's `YoutubeDL.py` docstring.

If downloads start failing (YouTube changes things regularly), the fix is
almost always just: `pip3 install -U yt-dlp`.

> Note: download only content you're allowed to save offline (your own
> purchases, freely licensed material, lectures, etc.) per YouTube's ToS.
