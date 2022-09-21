"""
Small custom client
"""

import aiohttp
import discord
from colorama import Fore, Style


class APHSClient(discord.Client):
    """
    Custom Client
    """

    def __init__(self) -> None:
        """
        Init the client
        """
        super().__init__(intents=discord.Intents.default())
        self.tree: discord.app_commands.CommandTree = discord.app_commands.CommandTree(
            self
        )
        self.config: dict
        self.session: aiohttp.ClientSession()

    async def setup_hook(self) -> None:
        """
        On setup sync commands
        """
        print(f"{Fore.YELLOW}Syncing commands up with discord...{Style.RESET_ALL}")
        await self.tree.sync()
        print(f"{Fore.GREEN}Done{Style.RESET_ALL}")
