import discord


class MessageHandler:
    async def send_message(
        self,
        ctx_or_interaction,
        content,
        *,
        ephemeral: bool = False,
    ):
        if isinstance(ctx_or_interaction, discord.Interaction):
            try:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(
                        content, ephemeral=ephemeral
                    )
                else:
                    await ctx_or_interaction.followup.send(content, ephemeral=ephemeral)
                return
            except discord.errors.InteractionResponded:
                try:
                    await ctx_or_interaction.followup.send(content, ephemeral=ephemeral)
                    return
                except Exception:
                    pass
            except discord.errors.NotFound:
                try:
                    await ctx_or_interaction.followup.send(content, ephemeral=ephemeral)
                    return
                except Exception:
                    pass
            except Exception:
                try:
                    await ctx_or_interaction.followup.send(content, ephemeral=ephemeral)
                    return
                except Exception:
                    pass

            try:
                user = getattr(ctx_or_interaction, "user", None) or getattr(
                    ctx_or_interaction, "author", None
                )
                if user:
                    await user.send(content)
                    return
            except Exception:
                pass

            print("[MessageHandler] failed to send interaction message:", content)
        else:
            await ctx_or_interaction.send(content)
