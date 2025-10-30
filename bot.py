import discord
from discord.ext import commands
from config import TOKEN
from utils.i18n import t
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)
tree = bot.tree


async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")


@bot.event
async def on_ready():
    await load_cogs()
    await tree.sync()
    print(t("bot_ready", bot=bot.user))


bot.run(TOKEN)
