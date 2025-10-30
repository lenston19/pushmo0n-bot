# pushmo0n-bot

Lightweight Discord music and moderation bot built with `discord.py`. Uses `yt-dlp` + `ffmpeg` for audio playback.

Summary:
- Play audio from the internet
- Queue management and basic playback controls
- Modular structure using `cogs`

## Quick start

1. Clone the repository and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root (see `.env.example`). By default the bot messages are English; to enable Russian set `LANGUAGE=ru`.

4. Run the bot:

```powershell
python bot.py
```

## Configuration (.env)

Example `.env`:

```
DISCORD_TOKEN=your_discord_bot_token
# Optional: LANGUAGE=ru  # default is English (en)
```

`LANGUAGE` values:
- `ru` — Russian messages
- any other value or unset — English (default)

## Requirements

- Python 3.10+
- `ffmpeg` installed and available in PATH
- Internet access (for downloading/streaming via `yt-dlp`)

## Project structure

- `bot.py` — entry point
- `config.py` — environment variables and settings
- `cogs/` — extensions (music, moderation, etc.)
- `utils/` — helper modules (ytdl, voice, message_handler, i18n)

## Commands

Below is a table of the bot's main commands. These are implemented as slash commands; prefix commands may also be available depending on configuration.

| Command           |  Type | Parameters                        | Description                                                           |
| ----------------- | ----: | --------------------------------- | --------------------------------------------------------------------- |
| `/join`           | slash | —                                 | Connect the bot to your voice channel                                 |
| `/leave`          | slash | —                                 | Disconnect the bot from the voice channel                             |
| `/play <query>`   | slash | query: str                        | Play a track by URL or search query; adds to queue if already playing |
| `/skip`           | slash | —                                 | Skip the current track                                                |
| `/stop`           | slash | —                                 | Stop playback and disconnect the bot                                  |
| `/pause`          | slash | —                                 | Pause the current track                                               |
| `/resume`         | slash | —                                 | Resume playback if paused                                             |
| `/shuffle`        | slash | —                                 | Shuffle the current queue                                             |
| `/now`            | slash | —                                 | Show the currently playing track                                      |
| `/queue`          | slash | —                                 | Show the current queue                                                |
| `/repeat <mode>`  | slash | mode: one of `none`, `one`, `all` | Set repeat mode                                                       |
| `/clear <amount>` | slash | amount: int                       | (Moderation) Delete recent messages (admin only)                      |

Notes:
- `/play` accepts both URLs and search queries (depends on `yt-dlp` behavior).
- `/repeat` modes: `none` — no repeat, `one` — repeat current track, `all` — loop the queue.
- `/clear` is restricted to administrators.

## Localization

Basic localization is available via `utils/i18n.py`. The current language default is taken from `config.DEFAULT_LANGUAGE` (set from `LANGUAGE` in `.env`). If you want to add translations, extend `utils/i18n.py` with more keys and languages.

## Docker

This repository includes a `Dockerfile` that installs Python, project dependencies and `ffmpeg` (used for audio playback). Below are examples to build and run the bot with Docker.

Build the image (from the project root):

```powershell
docker build -t pushmo0n-bot .
```

Run the container using an env file (recommended):

```powershell
docker run -d --name pushmo0n-bot --env-file .env pushmo0n-bot
```

Or pass the token directly (less secure):

```powershell
docker run -d --name pushmo0n-bot -e DISCORD_TOKEN="your_token_here" pushmo0n-bot
```

Notes:
- The image installs `ffmpeg` in the container (see `Dockerfile`), so you don't need host ffmpeg.
- Use `--restart unless-stopped` with `docker run` for automatic restart after reboots:

```powershell
docker run -d --restart unless-stopped --name pushmo0n-bot --env-file .env pushmo0n-bot
```

