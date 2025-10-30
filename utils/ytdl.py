import yt_dlp
from config import YTDL_OPTIONS

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


async def get_audio_info(query):
    """Возвращает URL аудио и название трека"""
    if not query.startswith("http"):
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
    else:
        info = ytdl.extract_info(query, download=False)
    audio_url = info["url"]
    title = info.get("title", "Untitled")
    return {"audio_url": audio_url, "title": title}
