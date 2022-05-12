from __future__ import print_function

import json

from discord.ext import commands, tasks
import discord
import datetime

from gears.docs import Docs


class AnnouncementsDB:
    """
    Read from the announcements json document/mongodb whenever I update it
    """

    def __init__(self) -> None:
        """
        Nothing to add here as of yet
        """
        pass

    async def get_latest_day(self) -> list:
        """Get latest days list of announcements"""
        with open("info/a_info.json", "r", encoding="utf8") as file:
            latest_json = json.loads(file.read())

        first_key = latest_json.keys()

        a_list = latest_json.get(list(first_key)[0])

        return a_list

    async def get_day(self, day: int) -> list:
        """Get a certain days announcement"""
        with open("info/a_info.json", "r", encoding="utf8") as file:
            latest_json = json.loads(file.read())
        day -= 1
        keys = list(latest_json.keys)
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

    def cog_unload(self):
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
            a_list = await self.ajson.get_latest_day()

            a_formatted = ""

            for announcement in a_list:
                announcements = f"""{a_formatted}\n+ {announcement}"""

            embed = discord.Embed(
                title=f"Todays Announcements",
                description=f"""```diff
{announcements}
```""",
                timestamp=datetime.datetime.utcnow(),
                color=ctx.author.color,
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Announcements(bot))
