import discord
from discord.ext import commands, tasks
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

async def cache_afk_messages(bot, main):
    """A function that caches our stuff"""
    # creating a new dict so we don't interfere with other data until its completely finished.
    afk_dict = {}
    cursor = main.find()
    for document in await cursor.to_list(length=300):
        afk_dict[document.get("_id")] = document.get("message")
    bot.afk_dict = afk_dict

class Ping(commands.Cog):
    """Cog Example Description"""
    def __init__(self, bot):
        self.bot = bot
        # The actual db
        self.db = bot.mongo["Ping"]
        # The collection in which we store all the main stuff
        self.main = self.db["Main"]
        self.afk_cacher.start()

    def cog_unload(self):
        self.afk_cacher.cancel()

    @tasks.loop(minutes=10)
    async def afk_cacher(self):
        """Recache our afk_dict every 10 min"""
        await cache_afk_messages(self.bot, self.main)
        

    @commands.Cog.listener()
    async def on_message(self, msg):
        """Tracking all messages to see when we need to respond..."""
        # ignore ourself since we don't wanna do recursion
        if msg.author == self.bot.user:
            return
        for user_id in self.bot.afk_dict.keys().copy():
            user_id = int(user_id)

            member = msg.guild.get_member(user_id)

            if member.mentioned_in(msg):
                embed = discord.Embed(
                    title=f"{member.display_name} is AFK",
                    description=self.bot.afk_dict.get(user_id),
                    timestamp=datetime.datetime.utcnow(),
                    color=msg.author.color
                )
                await msg.channel.send(embed=embed)

            if msg.author.id == user_id:
                del self.bot.afk_dict[user_id]
                await self.main.delete_one({"_id": msg.author.id})
                embed = discord.Embed(
                    title=f"Welcome Back!",
                    description=f"""I have removed your afk for you {msg.author.mention}!""",
                    timestamp=datetime.datetime.utcnow(),
                    color=msg.author.color
                )
                return await msg.channel.send(embed=embed)

            
            
            
    @cog_ext.cog_slash(
        name="afk_set",
        description="""Set an afk message""",
        guild_ids=[754108375536762880],
        options=[
            create_option(
                name="message",
                description="The message that gets sent when you're pinged or mentioned",
                option_type=3,
                required=True
            )
        ]
    )
    async def _afk_set(self, ctx: SlashContext, message):
        """Set an afk message"""
        document = await self.main.find_one({"_id": ctx.author.id})
        self.bot.afk_dict[ctx.author.id] = message
        if not document:
            new_document = {
                "_id": ctx.author.id,
                "message": message
            }
            await self.main.insert_one(new_document)
        
        else:
            await self.main.update_one({"_id": ctx.author.id}, {"$set": {"message": message}})

        embed = discord.Embed(
            title=f"Set AFK Message",
            description=message,
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Ping(bot))