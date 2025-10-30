import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
import asyncio
import random

from utils.ytdl import get_audio_info
from utils.voice import ensure_voice
from config import FFMPEG_OPTIONS
from utils.i18n import t
from utils.message_handler import MessageHandler


queues = {}  # guild_id: [треков]
repeat_mode = {}  # guild_id: "none" / "one" / "all"
current_track = {}  # guild_id: текущий трек


class Music(commands.Cog, MessageHandler):
    def __init__(self, bot):
        self.bot = bot

    def add_to_queue(self, guild_id, track):
        if guild_id not in queues:
            queues[guild_id] = []
        queues[guild_id].append(track)

    async def play_song(self, ctx_or_interaction, query, status_message=None):
        try:
            info = await get_audio_info(query)
            audio_url = info["audio_url"]
            title = info["title"]
        except Exception as e:
            if status_message:
                await status_message.edit(content=t("failed_stream", error=e))
            else:
                await self.send_message(ctx_or_interaction, t("failed_stream", error=e))
            return

        if not await ensure_voice(ctx_or_interaction):
            if status_message:
                await status_message.edit(content=t("not_in_voice"))
            else:
                await self.send_message(ctx_or_interaction, t("not_in_voice"))
            return

        guild_id = ctx_or_interaction.guild.id
        vc = ctx_or_interaction.guild.voice_client

        if vc.is_playing():
            self.add_to_queue(guild_id, query)
            if status_message:
                await status_message.edit(content=t("added_queue", title=title))
            else:
                await self.send_message(
                    ctx_or_interaction,
                    t("added_queue", title=title),
                )
            return

        current_track[guild_id] = query
        source = FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

        def after_play(err):
            if err:
                print(f"Error playing: {err}")
            asyncio.run_coroutine_threadsafe(
                self.play_next(ctx_or_interaction), self.bot.loop
            )

        vc.play(source, after=after_play)

        if status_message:
            await status_message.edit(content=t("now_playing", title=title))
        else:
            await self.send_message(ctx_or_interaction, t("now_playing", title=title))

    async def play_next(self, ctx_or_interaction):
        guild_id = ctx_or_interaction.guild.id
        vc = ctx_or_interaction.guild.voice_client
        q = queues.get(guild_id, [])
        mode = repeat_mode.get(guild_id, "none")

        if not vc:
            return

        next_track = None
        if mode == "one":
            next_track = current_track.get(guild_id)
        elif mode == "all":
            if q:
                next_track = q.pop(0)
                q.append(next_track)
            else:
                next_track = current_track.get(guild_id)
        else:
            if q:
                next_track = q.pop(0)

        if next_track:
            await self.play_song(ctx_or_interaction, next_track)

    @app_commands.command(name="join", description=t("join_desc"))
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await self.send_message(interaction, t("not_in_voice"))
            return
        await interaction.user.voice.channel.connect()

    @app_commands.command(name="leave", description=t("leave_desc"))
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        try:
            await interaction.response.defer(thinking=True)
        except Exception:
            pass

        if vc:
            try:
                await vc.disconnect()
            except Exception as e:
                print(f"[leave] disconnect error: {e}")
            try:
                await interaction.followup.send(t("buy"))
            except Exception:
                await self.send_message(interaction, t("buy"))
        else:
            await self.send_message(interaction, t("bot_not_connected"))

    @app_commands.command(name="play", description=t("play_desc"))
    async def play(self, interaction: discord.Interaction, query: str):
        try:
            await interaction.response.defer(thinking=True)
            status_message = await interaction.followup.send(
                t("searching_track"),
                wait=True,
            )
        except Exception:
            try:
                await interaction.response.send_message(t("searching_track"))
                status_message = await interaction.original_response()
            except Exception:
                status_message = None

        await self.play_song(interaction, query, status_message=status_message)

    @app_commands.command(name="skip", description=t("skip_desc"))
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await self.play_next(interaction)
        else:
            await self.send_message(interaction, t("nothing_playing"))

    @app_commands.command(name="stop", description=t("stop_desc"))
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            queues[interaction.guild.id] = []
            await vc.disconnect()
        else:
            await self.send_message(interaction, t("bot_not_connected"))

    @app_commands.command(name="pause", description=t("pause_desc"))
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
        else:
            await self.send_message(interaction, t("nothing_playing"))

    @app_commands.command(name="resume", description=t("resume_desc"))
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
        else:
            await self.send_message(interaction, t("not_paused"))

    @app_commands.command(name="shuffle", description=t("shuffle_desc"))
    async def shuffle(self, interaction: discord.Interaction):
        q = queues.get(interaction.guild.id, [])
        if q:
            random.shuffle(q)
            text = "\n".join(f"{i + 1}. {url}" for i, url in enumerate(q))
            await self.send_message(interaction, t("queue_shuffled", text=text))
        else:
            await self.send_message(interaction, t("queue_empty"))

    @app_commands.command(name="now", description=t("now_desc"))
    async def now(self, interaction: discord.Interaction):
        track = current_track.get(interaction.guild.id)
        if track:
            await self.send_message(interaction, t("now_playing", title=track))
        else:
            await self.send_message(interaction, t("nothing_playing"))

    @app_commands.command(name="queue", description=t("queue_desc"))
    async def queue(self, interaction: discord.Interaction):
        q = queues.get(interaction.guild.id, [])
        if q:
            text = "\n".join(f"{i + 1}. {url}" for i, url in enumerate(q))
            await self.send_message(interaction, t("queue_list", text=text))
        else:
            await self.send_message(interaction, t("queue_empty"))

    @app_commands.command(name="repeat", description=t("repeat_desc"))
    async def repeat(self, interaction: discord.Interaction, mode: str):
        if mode not in ("none", "one", "all"):
            await self.send_message(interaction, t("invalid_repeat"))
            return
        repeat_mode[interaction.guild.id] = mode
        await self.send_message(interaction, t("repeat_set", mode=mode))


async def setup(bot):
    await bot.add_cog(Music(bot))
