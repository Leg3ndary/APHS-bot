"""
Small custom client
"""

import discord


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

    async def setup_hook(self) -> None:
        """
        On setup sync commands
        """
        print("Syncing commands")
        await self.tree.sync()
        print("Done")
