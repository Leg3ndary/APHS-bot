from discord.ext import commands
import discord
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

config = json.load(open("credentials/config.json"))

bot = commands.Bot(
    command_prefix="!!",
    description="The coolest bot ever",
    activity=discord.Game(name="!!help"),
    intents=discord.Intents.all(),
)


async def start_bot():
    """
    Start the bot
    """
    async with bot:
        bot.config = config
        print("Loaded Bot Config")

        mongo_uri = (
            config.get("Mongo")
            .get("URI")
            .replace("<Username>", config.get("Mongo").get("User"))
            .replace("<Password>", config.get("Mongo").get("Pass"))
        )

        bot.mongo = AsyncIOMotorClient(mongo_uri)
        print("Loaded Bot DB")

        cog_list = []
        for file in os.listdir("Bot/cogs"):
            try:
                if file.endswith(".py"):
                    await bot.load_extension(f"cogs.{file[:-3]}")
                    cog_list.append(f"cogs.{file[:-3]}")
                    print(f"Loaded {file[:-3]}")
            except Exception as e:
                print(f"Cog {file[:-3]} failed loading\nError: {e}")

        bot.cog_list = cog_list

        @bot.event
        async def on_ready():
            """On ready tell us"""
            await bot.wait_until_ready()
            print(f"Bot {bot.user} has logged in")

        await bot.start(config.get("Bot").get("Token"))


asyncio.run(start_bot())
