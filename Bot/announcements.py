"""
Announcements related classes
"""

import datetime
import json
from typing import Dict, List


class AnnouncementsDB:
    """
    Read from the announcements json document/mongodb whenever I update it
    """

    def __init__(self) -> None:
        """
        Init the class
        """
        self.latest: Dict[str, str] = None
        self.choices: List[str] = None

    async def update_latest(self) -> None:
        """
        Update latest announcements
        """
        with open("data/announcements.json", "r", encoding="utf8") as file:
            self.latest = json.loads(file.read())
            self.choices = self.latest.keys()

    async def get_latest(self) -> Dict[str, str]:
        """
        Get todays code
        """
        if datetime.datetime.now().weekday() in (5, 6):
            altered = datetime.datetime.now() - datetime.timedelta(
                days=1 if datetime.datetime.now().weekday() == 5 else 2
            )
            day = altered.strftime("%A %B %d")
        else:
            day = datetime.datetime.now().strftime("%A %B %d")
        return self.latest.get(day, {"No Announcements": "No Announcements"})
