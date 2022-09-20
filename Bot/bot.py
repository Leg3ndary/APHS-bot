import asyncio
import json

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


@announcements_group.command(name="today", description="Get todays announcements")
async def announcements_today_cmd(interaction: discord.Interaction) -> None:
    """
    Show todays announcements
    """
    a_list = await announce_db.get_latest_day()

    a_formatted = ""
    lday = await announce_db.get_today()

    for a_name, a_a in a_list.items():
        announcements = f"""{a_formatted}\n+ {a_name} - {a_a}"""

    embed = discord.Embed(
        title=f"{lday} Announcements",
        description=f"""```diff
{announcements}
```""",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


bot.tree.add_command(announcements_group)

announce_doc = Docs()
announce_db = AnnouncementsDB()


@bot.event
async def on_ready() -> None:
    """
    On ready tell us
    """
    await bot.wait_until_ready()
    print(f"Bot {bot.user} has logged in")

    print("Starting Doc Save")
    await announce_doc.save_doc()
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
