import discord
from discord.ext import commands
from discord import app_commands
from utils.message_handler import MessageHandler
from utils.i18n import t


class Moderation(commands.Cog, MessageHandler):
    def __init__(self, bot):
        self.bot = bot

    async def admin_only(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await self.send_message(interaction, t("admin_only"))
            return False
        return True

    @app_commands.command(name="clear", description=t("clear_desc"))
    @app_commands.describe(amount=t("amount_desc"))
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if not await self.admin_only(interaction):
            return
        await interaction.channel.purge(limit=amount + 1)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
