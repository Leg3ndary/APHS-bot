import asyncio
import datetime
import json
from typing import List

import aiohttp
import discord
import pytz
from announcements import AnnouncementsDB
from aphs_client import APHSClient
from discord.ext import tasks
from docs import Docs

with open("credentials/config.json", "r", encoding="utf8") as credentials:
    config = json.loads(credentials.read())

bot = APHSClient()

announcements_group: discord.app_commands.Group = discord.app_commands.Group(
    name="announcements", description="Get announcements"
)
announce_doc = Docs()
announce_db = AnnouncementsDB()


@announcements_group.command(name="today", description="Get todays announcements")
async def announcements_today_cmd(interaction: discord.Interaction) -> None:
    """
    Show todays announcements
    """
    todays_announcements = await announce_db.get_today()

    embed = discord.Embed(
        title="Todays Announcements",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    for name, announcement in todays_announcements.items():
        if name != "timestamp":
            embed.add_field(name=name, value=announcement, inline=False)
    await interaction.response.send_message(embed=embed)


async def on_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[discord.app_commands.Choice[str]]:
    """
    The autocomplete function for specific days
    """
    return [
        discord.app_commands.Choice(name=choice, value=choice)
        for choice in announce_db.choices
        if current.lower() in choice.lower()
    ]


@announcements_group.command(name="on", description="Announcements on a specific day")
@discord.app_commands.autocomplete(day=on_autocomplete)
async def announcements_on_cmd(interaction: discord.Interaction, day: str) -> None:
    """
    Show a certain days announcements
    """
    days_announcements = announce_db.latest.get(
        day, {"No Announcements": "No Announcements"}
    )

    embed = discord.Embed(
        title=f"{day} Announcements",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    for name, announcement in days_announcements.items():
        if name != "timestamp":
            embed.add_field(name=name, value=announcement, inline=False)
    await interaction.response.send_message(embed=embed)


@tasks.loop(time=datetime.time(hour=10, tzinfo=pytz.timezone("EST")))
async def update_announcements() -> None:
    """
    Update our announcements documents every day at 10am EST
    """
    print("Sending Announcements")
    await announce_doc.save_doc()
    await asyncio.sleep(1)  # just in case buffering
    await announce_db.update_latest()
    await asyncio.sleep(1)

    webhook = discord.Webhook.from_url(
        url=bot.config.get("Bot").get("AnnouncementsWebhook"), session=bot.session
    )
    todays_announcements = await announce_db.get_today()

    embed = discord.Embed(
        title="Todays Announcements",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    for name, announcement in todays_announcements.items():
        if name != "timestamp":
            embed.add_field(name=name, value=announcement, inline=False)

    await webhook.send(embed=embed)


bot.tree.add_command(announcements_group)


@bot.event
async def on_ready() -> None:
    """
    On ready tell us
    """
    await bot.wait_until_ready()
    print(f"Bot {bot.user} has logged in")

    print("Starting Doc Save")
    await announce_doc.save_doc()
    await announce_db.update_latest()
    print("Finished save and organization")
    update_announcements.start()


async def start_bot() -> None:
    """
    Start the bot
    """
    async with bot:
        bot.config = config
        print("Set Bot Config")
        bot.session = aiohttp.ClientSession()

        await bot.start(config.get("Bot").get("Token"))


asyncio.run(start_bot())
