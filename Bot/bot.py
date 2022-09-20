import asyncio
import datetime
import json

import discord
from docs import Docs

with open("credentials/config.json", "r", encoding="utf8") as credentials:
    config = json.loads(credentials.read())

class APHSClient(discord.Client):
    """
    Custom Client
    """

    def __init__(self) -> None:
        """
        Init the client
        """
        super().__init__(intents=discord.Intents.default())
        self.tree: discord.app_commands.CommandTree = discord.app_commands.CommandTree(self)
        self.config: dict

    async def setup_hook(self) -> None:
        """
        On setup sync commands
        """
        self.tree.copy_global_to(guild=discord.Object(id=839605885700669441))
        await self.tree.sync()


class AnnouncementsDB:
    """
    Read from the announcements json document/mongodb whenever I update it
    """

    async def get_today(self) -> str:
        """
        Get todays code
        """
        lday = (
            datetime.date.today()
            .strftime("%A %B %d &Y")
            .replace("01", "1")
            .replace("02", "2")
            .replace("03", "3")
            .replace("04", "4")
            .replace("05", "5")
            .replace("06", "6")
            .replace("07", "7")
            .replace("08", "8")
            .replace("09", "9")
            .replace("&Y", datetime.date.today().strftime("%Y"))
            .upper()
        )

        if "SATURDAY" in lday:
            lday = lday.replace("SATURDAY", "FRIDAY").replace(
                f" {int(datetime.date.today().strftime('%d'))} ",
                f" {int(datetime.date.today().strftime('%d')) - 1} ",
            )

        elif "SUNDAY" in lday:
            lday = lday.replace("SUNDAY", "FRIDAY").replace(
                f" {int(datetime.date.today().strftime('%d'))} ",
                f" {int(datetime.date.today().strftime('%d')) - 2} ",
            )

        return lday

    async def get_latest_day(self) -> dict:
        """
        Get latest days dict of announcements
        """
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
            lday = await self.get_today()
            a_list = latest.get(lday)

            return a_list

    async def get_day(self, day: int) -> list:
        """
        Get a certain days announcement
        """
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
        day -= 1
        keys = list(latest.keys)
        return keys[day]

    async def get_all(self) -> dict:
        """
        Get all announcements possible
        """


bot = APHSClient()

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


announcements_group: discord.app_commands.Group = discord.app_commands.Group(name="announcements", description="Get announcements")

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


asyncio.run(start_bot())
