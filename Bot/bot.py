import asyncio
import json
from typing import List

import discord
from announcements import AnnouncementsDB
from aphs_client import APHSClient
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


bot.tree.add_command(announcements_group)


@bot.event
async def on_ready() -> None:
    """
    On ready tell us
    """
    await bot.wait_until_ready()
    print(f"Bot {bot.user} has logged in")

    print("Starting Doc Save")
    # await announce_doc.save_doc()
    await announce_db.update_latest()
    print("Finished save and organization")


async def start_bot() -> None:
    """
    Start the bot
    """
    async with bot:
        bot.config = config
        print("Set Bot Config")

        await bot.start(config.get("Bot").get("Token"))


asyncio.run(start_bot())
