import asyncio
import datetime
import json
from typing import List

import aiohttp
import discord
from announcements import AnnouncementsDB
from aphs_client import APHSClient
from colorama import Fore, Style
from courses import CoursesManager
from discord.ext import tasks
from docs import Docs

with open("credentials/config.json", "r", encoding="utf8") as credentials:
    config = json.loads(credentials.read())

bot = APHSClient()

announcements_group: discord.app_commands.Group = discord.app_commands.Group(
    name="announcements", description="Announcements related commands"
)
announce_doc = Docs()
announce_db = AnnouncementsDB()


@announcements_group.command(name="latest", description="Get the latest announcements")
async def announcements_today_cmd(interaction: discord.Interaction) -> None:
    """
    Show the latest announcements
    """
    latest = await announce_db.get_latest()

    announcement_date = datetime.datetime.fromtimestamp(latest.get("timestamp"))

    embed = discord.Embed(
        title=f"{announcement_date.strftime('%A %B %d')}",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    for name, announcement in latest.items():
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
    ][:25]


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


@tasks.loop(time=datetime.time(hour=13, minute=25, second=0))
async def update_announcements() -> None:
    """
    Update our announcements documents every day at 9:25am EST
    """
    if datetime.datetime.now().weekday() in (5, 6):
        return
    await announce_doc.save_doc()
    await announce_db.update_latest()
    print("Updated latest announcements")

    webhook = discord.Webhook.from_url(
        url=bot.config.get("Bot").get("AnnouncementsWebhook"), session=bot.session
    )

    latest = await announce_db.get_latest()

    announcement_date = datetime.datetime.fromtimestamp(latest.get("timestamp"))

    embed = discord.Embed(
        title=f"{announcement_date.strftime('%A %B %d')}",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.blue(),
    )
    for name, announcement in latest.items():
        if name != "timestamp":
            embed.add_field(name=name, value=announcement, inline=False)

    await webhook.send(embed=embed)


bot.tree.add_command(announcements_group)


courses_group: discord.app_commands.Group = discord.app_commands.Group(
    name="courses", description="Course related commands"
)
course_manager = CoursesManager()


async def course_code_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[discord.app_commands.Choice[str]]:
    """
    The autocomplete function for course codes
    """
    return [
        discord.app_commands.Choice(name=choice, value=choice)
        for choice in course_manager.course_codes
        if current.lower() in choice.lower()
    ][:25]


@courses_group.command(
    name="code", description="Search for a course by it's corresponding course code"
)
@discord.app_commands.autocomplete(code=course_code_autocomplete)
async def courses_code_cmd(interaction: discord.Interaction, code: str) -> None:
    """
    Find a course by it's code
    """
    course = [
        course for course in course_manager.courses if course.course_code == code
    ][0]

    embed = discord.Embed(
        title=f"{course.name}",
        description=course.description.replace("\n", ""),
        timestamp=discord.utils.utcnow(),
        color=discord.Color.yellow(),
    )
    embed.add_field(name="Prerequisites", value=course.prerequisites, inline=False)
    embed.add_field(
        name="Grading Breakdown",
        value=f"""```yaml
Knowledge/Understanding: {course.knowledge_understanding}%
Application:             {course.application}%
Thinking:                {course.thinking}%
Communication:           {course.communication}%

Performance Task:        {course.performance_task}%
Final Exam:              {course.final_exam}%

Total:                   {course.total}%
```""",
        inline=False,
    )
    embed.add_field(
        name="Additional Details", value=course.additional_details, inline=False
    )
    embed.set_author(
        name=f"{course.course_code} - Exam Length: {course.evaluation_duration}"
    )
    embed.set_footer(text=f"Last Revised {course.last_revision}")
    await interaction.response.send_message(embed=embed)


async def course_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[discord.app_commands.Choice[str]]:
    """
    The autocomplete function for course codes
    """
    return [
        discord.app_commands.Choice(name=choice, value=choice)
        for choice in course_manager.course_names
        if current.lower() in choice.lower()
    ][:25]


@courses_group.command(name="name", description="Search for a course by it's name")
@discord.app_commands.autocomplete(name=course_name_autocomplete)
async def courses_name_cmd(interaction: discord.Interaction, name: str) -> None:
    """
    Find a course by it's name
    """
    course = [course for course in course_manager.courses if course.name == name][0]

    embed = discord.Embed(
        title=f"{course.name}",
        description=course.description.replace("\n", ""),
        timestamp=discord.utils.utcnow(),
        color=discord.Color.yellow(),
    )
    embed.add_field(name="Prerequisites", value=course.prerequisites, inline=False)
    embed.add_field(
        name="Grading Breakdown",
        value=f"""```yaml
Knowledge/Understanding: {course.knowledge_understanding}%
Application:             {course.application}%
Thinking:                {course.thinking}%
Communication:           {course.communication}%

Performance Task:        {course.performance_task}%
Final Exam:              {course.final_exam}%

Total:                   {course.total}%
```""",
        inline=False,
    )
    embed.add_field(
        name="Additional Details", value=course.additional_details, inline=False
    )
    embed.set_author(
        name=f"{course.course_code} - Exam Length: {course.evaluation_duration}"
    )
    embed.set_footer(text=f"Last Revised {course.last_revision}")
    await interaction.response.send_message(embed=embed)


bot.tree.add_command(courses_group)


@bot.event
async def on_ready() -> None:
    """
    On ready tell us
    """
    await bot.wait_until_ready()
    print(f"{Fore.CYAN}Bot {bot.user} has logged on.{Style.RESET_ALL}")

    print(
        f"{Fore.YELLOW}Saving announcements to data/announcements.json and data/announcements.md...{Style.RESET_ALL}"
    )
    await announce_doc.save_doc()
    await announce_db.update_latest()
    print(f"{Fore.GREEN}Finished.{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}Building courses and related data...{Style.RESET_ALL}")
    await course_manager.build_courses()
    print(f"{Fore.GREEN}Finished.{Style.RESET_ALL}")
    update_announcements.start()


async def start_bot() -> None:
    """
    Start the bot
    """
    async with bot:
        bot.config = config
        bot.session = aiohttp.ClientSession()

        await bot.start(config.get("Bot").get("Token"))


asyncio.run(start_bot())
