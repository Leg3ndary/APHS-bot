import datetime
import json
import re

import googleapiclient.discovery
from httplib2 import Http
from oauth2client import client, file, tools


class Docs:
    """
    Class for accessing info about the announcements doc
    """

    def __init__(self) -> None:
        """
        Initiates with all the info that we need
        """
        self.text: str = None
        with open("credentials/config.json", "r", encoding="utf8") as credentials:
            config = json.loads(credentials.read())
        self.SCOPES = [
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]
        self.DISCOVERY_DOC = "https://docs.googleapis.com/$discovery/rest?version=v1"
        self.DOCUMENT_ID = config.get("Google").get("DOCID")

    async def convert_list_to_dict(self, olist: list) -> dict:
        """
        Convert list to a dict [item1, item2, item3, item4] = {item1: item2, item3: item4}

        Parameters
        ----------
        olist: list
            List

        Returns
        -------
        None
        """
        it = iter(olist)
        res_dct = dict(zip(it, it))
        return res_dct

    async def get_credentials(self) -> dict:
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Parameters
        ----------
        None

        Returns
        -------
        Credentials: dict
            The obtained credential.
        """
        store = file.Storage("credentials/token.json")
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                "credentials/credentials.json", self.SCOPES
            )
            credentials = tools.run_flow(flow, store)
        return credentials

    async def read_paragraph_element(self, element: dict) -> str:
        """
        Returns the text in the given ParagraphElement.

        Parameters
        ----------
        element: dict
            a ParagraphElement from a Google Doc.

        Returns
        -------
        str
            Parsed string
        """
        text_run = element.get("textRun")

        if not text_run:
            return ""

        text_style = text_run.get("textStyle")
        is_bolded = text_style.get("bold")
        is_underlined = text_style.get("underline")
        foreground = text_style.get("foregroundColor")
        if foreground:
            rgb_blue_color = foreground.get("color").get("rgbColor").get("blue")
        else:
            rgb_blue_color = None

        font_size = text_style.get("fontSize")
        if font_size:
            magnitude = font_size.get("magnitude")
        else:
            magnitude = None

        if "APHS DAILY ANNOUNCEMENTS" in text_run.get("content"):
            # For some reason the title shares the same stuff as days, so yes...
            return f"# {text_run.get('content', '')}"

        if is_bolded and is_underlined and rgb_blue_color == 1 and magnitude == 14:
            if text_run.get("content") == "\n":
                return text_run.get("content")
            return f"## {text_run.get('content', '')}"

        if is_bolded and magnitude == 10:
            return f"**{text_run.get('content', '').replace('-', '').strip()}**"

        return text_run.get("content", "")

    async def read_strucutural_elements(self, elements: list) -> None:
        """
        Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Parameters
        ----------
        elements: list
            a list of Structural Elements.

        Returns
        -------
        Not sure
        """
        text = ""
        with open("data/raw_elements.json", "w", encoding="utf8") as raw_elements:
            json.dump(elements, raw_elements, indent=4)
        flag = False
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")

                for elem in elements:
                    if elem.get("textRun"):
                        if "APHS DAILY ANNOUNCEMENTS - 2022 - 2023\n" in elem.get(
                            "textRun"
                        ).get("content"):
                            flag = True
                        elif "SCHOOL YEAR 2021 - 2022\n" in elem.get("textRun").get(
                            "content"
                        ):
                            flag = False
                    if flag:
                        text += await self.read_paragraph_element(elem)

            """
            This shouldn't ever happen, unless some teacher wants to add a table, uh oh.
            
            elif "table" in value:
                # The text in table cells are in nested Structural Elements and tables may be
                # nested.
                table = value.get("table")
                for row in table.get("tableRows"):
                    cells = row.get("tableCells")
                    for cell in cells:
                        text += await self.read_strucutural_elements(
                            cell.get("content")
                        )
            elif "tableOfContents" in value:
                # The text in the TOC is also in a Structural Element.
                toc = value.get("tableOfContents")
                text += await self.read_strucutural_elements(toc.get("content"))
            """

        return text

    async def save_doc(self):
        """
        Uses the Docs API to save the document to a md file

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        credentials = await self.get_credentials()
        http = credentials.authorize(Http())
        docs_service = googleapiclient.discovery.build(
            "docs", "v1", http=http, discoveryServiceUrl=self.DISCOVERY_DOC
        )
        doc = docs_service.documents().get(documentId=self.DOCUMENT_ID).execute()
        doc_content = doc.get("body").get("content")

        with open("data/announcements.md", "w", encoding="utf8") as announcements:
            # I don't know what this is, I should probably change to regex later
            text = (
                (await self.read_strucutural_elements(doc_content))
                .replace("\n****", "\n\n**")
                .replace("********", "**")
                .replace("******", "**")
                .replace("****", "**")
            )
            announcements.write(text)
            self.text = text

        await self.organize_doc()

    async def organize_doc(self) -> None:
        """
        Organize the text into a json file (announcements.json)

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        full = {}

        """ Painful regex that I had to learn and ask for help, keeping just in case I need it in the future
        edited_text = re.split(
            r"## ((?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY) (?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \b(?:[1-9]|[12][0-9]|3[01])\b (?:2021|2022))",
            edited_text,
        )
        """

        days_split = self.text.split("## ")

        del days_split[0]  # delete aphs daily announcements stuff

        for day in days_split:
            temp_announcements = {}
            for announcement in day.split("\n\n**")[1:]:
                a_info = list(filter(None, announcement.split("**")))
                if a_info:
                    if len(a_info) == 1:
                        pass
                    elif not a_info[0] == "\n":

                        cleansed = re.sub(r"^- ", "", a_info[1].strip())
                        if cleansed[0].isalpha():
                            if cleansed[0] == cleansed[0].lower():
                                cleansed = f"{a_info[0]} {cleansed}"
                        temp_announcements[a_info[0]] = cleansed

            day_info = day.split("\n\n")[0].strip().split(" ")
            day_name = day_info[0].capitalize()
            month = day_info[1][:3].capitalize()
            date = day_info[2].capitalize()
            year = datetime.datetime.now().year

            try:
                datetime_info = datetime.datetime.strptime(
                    f"{day_name} {month} {date} {year}", "%A %b %d %Y"
                )
            except ValueError:
                datetime_info = datetime.datetime.strptime(
                    f"{day_name} {month} {date} {year}", "%A %d %b %Y"
                )
            temp_announcements["timestamp"] = int(datetime_info.timestamp())

            full[
                datetime_info.strftime("%A %B %d")
            ] = temp_announcements  # this will fail in 2023 if they start adding the year.

        with open("data/announcements.json", "w", encoding="utf8") as announcements:
            json.dump(full, announcements, indent=4)
