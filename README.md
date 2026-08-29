# YYYClips

**🚀 Live at [https://yyyclips.up.railway.app](https://yyyclips.up.railway.app)**

A FastAPI web app for downloading media from YouTube, Instagram, and TikTok through `yt-dlp`. Inspect a URL, select your desired video resolution or audio bitrate, and download MP4 or MP3 files instantly. No installation needed—access it online!

## Features

- ✅ Download from YouTube, Instagram (including Reels), and TikTok
- ✅ Video resolutions up to 4K (when available)
- ✅ Audio extraction up to 320 kbps
- ✅ Support for vertical videos, squares, and landscapes
- ✅ Save quality preferences locally
- ✅ Livestream support
- ✅ Privacy & Terms pages
- ✅ 100% local processing (files not stored on servers)

## Run Locally

### Requirements

- Python 3.10+
- FFmpeg available on your system `PATH`

### Install FFmpeg

- **Windows:** `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS:** `brew install ffmpeg`
- **Debian/Ubuntu:** `sudo apt update && sudo apt install ffmpeg`

Confirm: `ffmpeg -version`

### Setup & Run

```powershell
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Deploy Online

See [DEPLOY.md](DEPLOY.md) for Railway, Render, or other cloud platforms.

## Legal

Only download content you have permission to access. Use YYYClips in accordance with each platform's terms of service. See [Privacy Policy](https://yyyclips.up.railway.app/privacy) and [Terms of Service](https://yyyclips.up.railway.app/terms).
