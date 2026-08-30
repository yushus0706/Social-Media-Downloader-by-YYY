from __future__ import annotations

import asyncio
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import yt_dlp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
SUPPORTED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be", "instagram.com", "www.instagram.com", "tiktok.com", "www.tiktok.com", "vm.tiktok.com"}
QUALITY_PATTERN = re.compile(r"^(?:4K(?: (?:Square|Vertical / Reel / Short))?|(?:360|480|720|1080|1440)p(?: (?:Square|Vertical / Reel / Short))?|(?:64|128|192|256|320) kbps(?: \((?:High Quality|Standard)\))?)$", re.IGNORECASE)
VIDEO_BUCKETS = ((2160, "4K"), (1440, "1440p"), (1080, "1080p"), (720, "720p"), (480, "480p"), (360, "360p"))
AUDIO_PRESETS = ["320 kbps (High Quality)", "256 kbps", "192 kbps", "128 kbps (Standard)"]
ASPECT_SUFFIXES = ("", " Square", " Vertical / Reel / Short")

app = FastAPI(title="YYYClips", version="1.0.0")


class InfoRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return validate_media_url(value)


class DownloadRequest(InfoRequest):
    format: Literal["mp4", "mp3"]
    quality: str = Field(min_length=2, max_length=64)

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, value: str) -> str:
        normalized = value.strip()
        if not QUALITY_PATTERN.fullmatch(normalized):
            raise ValueError("Quality must be a standard video or audio option.")
        return normalized


def validate_media_url(value: str) -> str:
    parsed = urlparse(value.strip())
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or hostname not in SUPPORTED_HOSTS:
        raise ValueError("Only YouTube, Instagram, and TikTok URLs are supported.")
    return value.strip()


def extraction_options() -> dict[str, Any]:
    return {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "live_from_start": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 60,
        "youtube_include_dash_manifest": True,
        "extractor_args": {
            "youtube": ["player_client=android", "player_client=web", "player_skip=webpage"],
            "instagram": ["prefer_highres"],
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }


def format_options(info: dict[str, Any]) -> tuple[list[str], list[str]]:
    formats = info.get("formats") or []
    resolutions = {
        label
        for item in formats
        if item.get("ext") == "mp4"
        and item.get("width")
        and item.get("height")
        for label in [video_bucket_label(float(item["width"]), float(item["height"]))]
        if label
    }
    ordered_resolutions = [
        f"{tier_label}{suffix}"
        for tier, tier_label in VIDEO_BUCKETS
        for suffix in ASPECT_SUFFIXES
        if f"{tier_label}{suffix}" in resolutions
    ]
    return ordered_resolutions, AUDIO_PRESETS.copy()


def video_bucket_label(width: float, height: float) -> str | None:
    dimension = width if height > width else height
    tier_label = nearest_bucket_label(dimension, VIDEO_BUCKETS)
    if not tier_label:
        return None
    if height > width:
        return f"{tier_label} Vertical / Reel / Short"
    if abs(width - height) / max(width, height) < 0.05:
        return f"{tier_label} Square"
    return tier_label


def nearest_bucket_label(value: float, buckets: tuple[tuple[int, str], ...]) -> str | None:
    if value <= 0:
        return None
    return min(buckets, key=lambda bucket: abs(bucket[0] - value))[1]


def quality_value(quality: str, media_format: Literal["mp4", "mp3"]) -> int:
    normalized = quality.strip().lower()
    if media_format == "mp4":
        if normalized.startswith("4k"):
            return 2160
        return int(normalized.split("p", 1)[0])
    return int(normalized.split(" ", 1)[0])


def extract_info(url: str) -> dict[str, Any]:
    attempts = [extraction_options()]
    fallback = extraction_options()
    fallback["extractor_args"] = {
        "youtube": ["player_client=ios", "player_client=tv_embedded", "player_client=web", "player_skip=webpage"],
        "instagram": ["prefer_highres"],
    }
    attempts.append(fallback)

    last_error: Exception | None = None
    for options in attempts:
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=False)
            if not info:
                raise RuntimeError("No media was found at this URL.")
            break
        except Exception as exc:
            last_error = exc
            lowered = str(exc).lower()
            if "sign in" not in lowered and "cookies" not in lowered and "unavailable" not in lowered and "private" not in lowered:
                raise RuntimeError(f"Unable to inspect this link: {friendly_error(exc)}") from exc
    else:
        if last_error is not None:
            raise RuntimeError(f"Unable to inspect this link: {friendly_error(last_error)}") from last_error
        raise RuntimeError("Unable to inspect this link: The media could not be discovered anonymously.")

    if not info:
        raise RuntimeError("No media was found at this URL.")
    resolutions, bitrates = format_options(info)
    return {
        "id": info.get("id"),
        "title": info.get("title") or "Untitled media",
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader") or info.get("channel") or "Unknown creator",
        "resolutions": resolutions or ["360p"],
        "bitrates": bitrates,
    }


def friendly_error(error: Exception) -> str:
    message = str(error).replace("ERROR: ", "").strip()
    lowered = message.lower()
    if "private" in lowered:
        return "This media is private or requires an account."
    if "geo" in lowered or "country" in lowered:
        return "This media is not available in your region."
    if "sign in" in lowered or "login" in lowered:
        return "This media requires sign-in and cannot be downloaded anonymously."
    if "not found" in lowered or "no video" in lowered:
        return "The media could not be found at this URL."
    return message[:300] or "The media service rejected this request."


def download_media(request: DownloadRequest, output_dir: Path) -> Path:
    output_template = str(output_dir / "%(title).120s [%(id)s].%(ext)s")
    target_quality = quality_value(request.quality, request.format)
    if request.format == "mp4":
        format_selector = f"bestvideo[height<={target_quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={target_quality}][ext=mp4]/best"
        options: dict[str, Any] = {
            "format": format_selector,
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "live_from_start": True,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "socket_timeout": 60,
            "youtube_include_dash_manifest": True,
            "extractor_args": {
                "youtube": ["player_client=android", "player_client=web", "player_skip=webpage"],
                "instagram": ["prefer_highres"],
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
        }
    else:
        options = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "live_from_start": True,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "socket_timeout": 60,
            "youtube_include_dash_manifest": True,
            "extractor_args": {
                "youtube": ["player_client=android", "player_client=web", "player_skip=webpage"],
                "instagram": ["prefer_highres"],
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": str(target_quality)}],
        }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([request.url])
    except Exception as exc:
        raise RuntimeError(f"Unable to download this media: {friendly_error(exc)}") from exc

    candidates = [path for path in output_dir.iterdir() if path.is_file() and path.suffix.lower() in {".mp4", ".mp3", ".m4a", ".webm"}]
    if not candidates:
        raise RuntimeError("The download finished without producing a file.")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def remove_directory(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse((TEMPLATES_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/privacy", response_class=HTMLResponse)
async def privacy() -> HTMLResponse:
    return HTMLResponse((TEMPLATES_DIR / "privacy.html").read_text(encoding="utf-8"))


@app.get("/terms", response_class=HTMLResponse)
async def terms() -> HTMLResponse:
    return HTMLResponse((TEMPLATES_DIR / "terms.html").read_text(encoding="utf-8"))


@app.post("/api/info")
async def media_info(request: InfoRequest) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(extract_info, request.url)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/download")
async def media_download(request: DownloadRequest, background_tasks: BackgroundTasks) -> FileResponse:
    output_dir = Path(tempfile.mkdtemp(prefix="yyyclips-"))
    try:
        media_path = await asyncio.to_thread(download_media, request, output_dir)
    except RuntimeError as exc:
        remove_directory(str(output_dir))
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    background_tasks.add_task(remove_directory, str(output_dir))
    media_type = "audio/mpeg" if request.format == "mp3" else "video/mp4"
    return FileResponse(media_path, media_type=media_type, filename=media_path.name, background=background_tasks)


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
