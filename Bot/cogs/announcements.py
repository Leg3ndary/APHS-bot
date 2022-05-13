import json
from discord.ext import commands, tasks
import discord
import datetime
from gears.docs import Docs
import pytz


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

    def filter_announcements(self, adict) -> None:
        """
        Filter announcements because mongodb is stupid
        """
        altered = adict.copy()
        for key in adict.keys():
            if "." in key:
                altered[key.replace(".", "/P/")] = altered.pop(key)

        return altered

    async def update_db(self) -> None:
        """
        Update our db with announcements that aren't found
        """
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())

            for date, announcements in latest.items():
                query = {"_id": date}

                filtered = self.filter_announcements(announcements)

                if not await self.main.find_one(query):
                    new_doc = {"_id": date, "date": date, "announcements": filtered}
                    await self.main.insert_one(new_doc)

            pipeline = [{"$addFields": {"date": {"$toDate": "$date"}}}]

            async for doc in self.main.aggregate(pipeline):
                await self.main.update_one(query, {"$set": {"date": doc.get("date")}})


class AnnouncementsDB:
    """
    Read from the announcements json document/mongodb whenever I update it
    """

    def __init__(self) -> None:
        """
        Nothing to add here as of yet
        """
        pass

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
        """Get latest days dict of announcements"""
        with open("info/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
            lday = await self.get_today()
            a_list = latest.get(lday)

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

    @tasks.loop(time=datetime.time(hour=10, tzinfo=pytz.timezone("EST")))
    async def update_announcements(self):
        """Update our announcements documents every 10 minutes"""
        await self.announce_doc.save_doc()
        await self.mongo.update_db()

    @commands.Cog.listener()
    async def on_ready(self):
        """On ready save the doc to our text file"""
        print("Starting Doc Save")
        await self.announce_doc.save_doc()
        await self.mongo.update_db()
        print("Finished save and organization")

    @commands.hybrid_group()
    async def announcements(self, ctx):
        """Show todays announcements"""
        if not ctx.invoked_subcommand:
            a_list = await self.announce_db.get_latest_day()

            a_formatted = ""
            lday = await self.announce_db.get_today()

            for a_name, a_a in a_list.items():
                announcements = f"""{a_formatted}\n+ {a_name} - {a_a}"""

            embed = discord.Embed(
                title=f"{lday} Announcements",
                description=f"""```diff
{announcements}
```""",
                timestamp=discord.utils.utcnow(),
                color=ctx.author.color,
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Announcements(bot))
