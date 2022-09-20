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

    async def get_today(self) -> Dict[str, str]:
        """
        Get todays code
        """
        today = datetime.datetime.now().strftime("%A %B %d")
        return self.latest.get(today, {"No Announcements": "No Announcements"})
