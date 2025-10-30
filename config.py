import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

DEFAULT_LANGUAGE = os.getenv("LANGUAGE", "en")

YTDL_OPTIONS = {
    "format": "bestaudio[ext=webm]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "nocheckcertificate": True,
    "geo_bypass": True,
}

FFMPEG_OPTIONS = {"options": "-vn"}
