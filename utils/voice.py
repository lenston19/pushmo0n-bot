import asyncio
from utils.i18n import t


async def ensure_voice(ctx_or_interaction, *, timeout: float = 5.0) -> bool:
    """Ensure the bot is connected to the same voice channel as the user.

    Returns True if the bot is connected or successfully connected/moved.
    Returns False if the user is not in a voice channel or connection failed.
    """
    user = getattr(ctx_or_interaction, "user", None) or getattr(
        ctx_or_interaction, "author", None
    )
    guild = ctx_or_interaction.guild

    if not guild.voice_client:
        if not getattr(user, "voice", None):
            msg = t("not_in_voice")
            send = getattr(
                ctx_or_interaction, "followup", getattr(ctx_or_interaction, "send")
            )
            try:
                if hasattr(send, "send"):
                    await send.send(msg)
                else:
                    await send(msg)
            except Exception:
                pass
            return False

        try:
            await user.voice.channel.connect()
        except Exception as e:
            print(f"[ensure_voice] failed to connect: {e}")
            return False

        total = 0.0
        while not guild.voice_client and total < timeout:
            await asyncio.sleep(0.1)
            total += 0.1
        if not guild.voice_client:
            print("[ensure_voice] timeout waiting for voice client")
            return False

    else:
        if (
            getattr(user, "voice", None)
            and guild.voice_client.channel != user.voice.channel
        ):
            try:
                await guild.voice_client.move_to(user.voice.channel)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"[ensure_voice] failed to move voice client: {e}")

    return True
