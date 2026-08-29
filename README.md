# YYYClips

A local FastAPI web app for downloading media from YouTube, Instagram, and TikTok through `yt-dlp`. The browser UI inspects a URL, shows available video resolutions or audio bitrates, then downloads an MP4 or MP3 file.

## Requirements

- Python 3.10+
- FFmpeg available on your system `PATH` (required for video merging and MP3 conversion)

### Install FFmpeg

- Windows: install with `winget install Gyan.FFmpeg` or download a build from [ffmpeg.org](https://ffmpeg.org/download.html), then add its `bin` folder to `PATH`.
- macOS: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt update && sudo apt install ffmpeg`

Confirm it works with `ffmpeg -version`.

## Run

```powershell
C:/Python314/python.exe -m pip install -r requirements.txt
C:/Python314/python.exe -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000.

The app processes downloads locally and does not bypass private, geo-restricted, or sign-in-only media. Use it only for content you have permission to download and in accordance with each platform's terms.
