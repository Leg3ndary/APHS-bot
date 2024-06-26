import os.path
from typing import List

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Course:
    """
    A course, when built you provide a list as that's just the simplist way to build it
    """

    def __init__(self, course: List[str]) -> None:
        """
        Build a course
        """
        self.course_code: str = course[0]
        self.outline: str = course[1]
        self.name: str = course[2]
        self.description: str = course[3]
        self.prerequisites: str = course[4]
        self.knowledge_understanding: str = course[5]
        self.application: str = course[6]
        self.thinking: str = course[7]
        self.communication: str = course[8]
        self.performance_task: str = course[9]
        self.final_exam: str = course[10]
        self.total: str = course[11]
        self.evaluation_duration: str = course[12]
        self.last_revision: str = course[13]
        self.additional_details: str = course[14]


class CoursesManager:
    """
    Class for accessing courses and course info
    """

    SPREADSHEET_ID: str = "12kpeZgDyE81n5PnxRcprslGKfaQfepzBVHkXg9IG3aw"
    RANGE_NAME: str = "A2:O320"  # All Courses as of 2022 when I made this
    SCOPES: List[str] = [
        "https://www.googleapis.com/auth/documents.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]

    courses: List[Course] = []
    course_codes: List[str] = []
    course_names: List[str] = []

    def __init__(self) -> None:
        """
        Run the flow
        """
        creds = None
        if os.path.exists("credentials/token2.json"):
            creds = Credentials.from_authorized_user_file(
                "credentials/token2.json", self.SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials/credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("credentials/token2.json", "w", encoding="utf8") as token:
                token.write(creds.to_json())
        self.creds = creds

    async def get_courses(self) -> List[List[str]]:
        """
        Get all courses
        """
        service = build("sheets", "v4", credentials=self.creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.SPREADSHEET_ID, range=self.RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        df = pd.DataFrame(values)
        df_replace = df.replace([""], [None])

        processed_dataset = df_replace.values.tolist()

        return processed_dataset

    async def build_courses(self) -> None:
        """
        Build courses
        """
        courses = await self.get_courses()
        for course in courses:
            self.courses.append(Course(course))
            self.course_codes.append(course[0])
            if course[2] is not None:
                self.course_names.append(course[2])
