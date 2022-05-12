import googleapiclient.discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import re
import json


class Docs:
    """Class for accessing info about the announcements doc"""

    def __init__(self) -> None:
        """
        Initiates with all the info that we need
        """
        self.SCOPES = "https://www.googleapis.com/auth/documents.readonly"
        self.DISCOVERY_DOC = "https://docs.googleapis.com/$discovery/rest?version=v1"
        self.DOCUMENT_ID = "1AsAPy6pVsB63S1u2B2PcdgI95FQEWufX-v0_hajAPzs"

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
        """Returns the text in the given ParagraphElement.

        Parameters
        ----------
        element: dict
            a ParagraphElement from a Google Doc.
        """
        text_run = element.get("textRun")

        if not text_run:
            return ""
        return text_run.get("content")

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
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")
                for elem in elements:
                    text += await self.read_paragraph_element(elem)
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
        return text

    async def save_doc(self):
        """
        Uses the Docs API to save the document to a txt file

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

        with open("info/a_info.txt", "w", encoding="utf8") as file:
            # json.dump(await self.read_strucutural_elements(doc_content), file, indent=4)
            text = await self.read_strucutural_elements(doc_content)
            file.write(text)
            self.text = text

    async def organize_doc(self) -> None:
        """
        Organize the text into a json file (a_info.json)

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        edited_text = self.text.replace("APHS DAILY ANNOUNCEMENTS\n\n\n\n", "")

        edited_text = re.split(
            r"((?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY) (?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) \b(?:[1-9]|[12][0-9]|3[01])\b (?:2021|2022))",
            edited_text,
        )

        del edited_text[0]

        organized_doc = self.convert_list_to_dict(edited_text)

        for item in organized_doc.keys():
            split_a = organized_doc.get(item).split("\n\n")
            del split_a[0]
            del split_a[-1]

            new_a_list = []

            for item_a in split_a:
                new_a_list.append(item_a.replace("\n", ""))

            organized_doc[item] = new_a_list

        with open("info/a_info.json", "w", encoding="utf8") as file:
            json.dump(organized_doc, file, indent=4)
