"""
Announcements related classes
"""

import datetime
import json


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
        with open("data/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
            lday = await self.get_today()
            a_list = latest.get(lday)

            return a_list

    async def get_day(self, day: int) -> list:
        """
        Get a certain days announcement
        """
        with open("data/announcements.json", "r", encoding="utf8") as file:
            latest = json.loads(file.read())
        day -= 1
        keys = list(latest.keys)
        return keys[day]

    async def get_all(self) -> dict:
        """
        Get all announcements possible
        """
