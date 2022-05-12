import json
from discord.ext import commands, tasks
import discord
import datetime
from gears.docs import Docs


class MongoInteract:
    """
    Some interactions with mongo that need a class
    """

    def __init__(self, mongo) -> None:
        """
        Init
        """
        self.db = mongo["Announcements"]
        self.main = self.db["Announcements"]

    async def update_db(self) -> None:
        """
        Update our db with announcements that aren't found
        """
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())


class AnnouncementsDB:
    """
    Read from the announcements json document/mongodb whenever I update it
    """

    def __init__(self) -> None:
        """
        Nothing to add here as of yet
        """
        pass

    async def get_latest_day(self) -> dict:
        """Get latest days dict of announcements"""
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())

        lday = datetime.datetime.strftime("%A %B %-d %Y").upper()

        if "SATURDAY" in lday:
            lday.replace("SATURDAY", "FRIDAY").replace(f" {datetime.datetime.strftime('%-d')} ", f" {int(datetime.datetime.strftime('%-d')) - 1} ")

        elif "SUNDAY" in lday:
            lday.replace("SUNDAY", "FRIDAY").replace(f" {datetime.datetime.strftime('%-d')} ", f" {int(datetime.datetime.strftime('%-d')) - 2} ")

        a_list = latest.get()

        return a_list

    async def get_day(self, day: int) -> list:
        """Get a certain days announcement"""
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
        day -= 1
        keys = list(latest.keys)
        return keys[day]

    async def get_all(self) -> dict:
        """Get all announcements possible"""
        pass


class Announcements(commands.Cog):
    """Announcements cog"""

    def __init__(self, bot):
        self.bot = bot
        self.announce_doc = Docs()
        self.announce_db = AnnouncementsDB()
        self.update_announcements.start()
        self.mongo = MongoInteract(bot.mongo)

    async def cog_unload(self):
        self.update_announcements.cancel()

    @tasks.loop(minutes=10)
    async def update_announcements(self):
        """Update our announcements documents every 10 minutes"""
        await self.announce_doc.save_doc()
        await self.announce_doc.organize_doc()

    @commands.Cog.listener()
    async def on_ready(self):
        """On ready save the doc to our text file"""
        print("Starting Doc Save")
        await self.announce_doc.save_doc()
        print("Doc saved to info/a_info.txt")
        await self.announce_doc.organize_doc()
        print("Json saved to info/a_info.json")

    @commands.hybrid_group()
    async def announcements(self, ctx):
        """Show todays announcements"""
        if not ctx.invoked_subcommand:
            a_list = await self.announce_db.get_latest_day()

            a_formatted = ""

            for day in a_list[a_list.keys()[0]]:
                for a_name, a_a in day.items():
                    announcements = f"""{a_formatted}\n+ {a_name} - {a_a}"""

            embed = discord.Embed(
                title=f"{a_list.keys()[0]} Announcements",
                description=f"""```diff
{announcements}
```""",
                timestamp=datetime.datetime.utcnow(),
                color=ctx.author.color,
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Announcements(bot))
