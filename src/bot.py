from discord.ext import commands
from discord_slash import SlashCommand
import discord
import os
from dotenv import load_dotenv
import json
from motor.motor_asyncio import AsyncIOMotorClient

config = json.load(open("src/config.json"))

load_dotenv()

bot = commands.Bot(
    command_prefix="!!",
    description="The coolest bot ever",
    activity=discord.Game(name="!!help"),
    intents=discord.Intents.all()
)
slash = SlashCommand(bot, sync_commands=True)

bot.config = config
print("Loaded Bot Config")

mongo_uri = config.get("Mongo_URL").replace("<Username>", config.get("Mongo_User")).replace("<Password>", os.getenv("Mongo_Pass"))

bot.mongo = AsyncIOMotorClient(mongo_uri)
print("Loaded Bot DB")

def load_cogs():
    """Generate a cog list based on the given cog directory"""
    cog_list = []
    for file in os.listdir("src/cogs"):
        try:
            if file.endswith(".py") and not file.endswith("cog_template.py"):
                bot.load_extension(f"cogs.{file[:-3]}")
                cog_list.append(f"cogs.{file[:-3]}")
                print(f"Loaded {file[:-3]}")

        except Exception as e:
            print(f"Cog {file[:-3]} failed loading\nError: {e}")

    bot.cog_list = cog_list

load_cogs()

@bot.event
async def on_ready():
    """On ready tell us"""
    print(f"Bot {bot.user} logged in yay")

bot.run(os.getenv("Bot_Token"))