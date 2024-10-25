"""
A simple cog that pings the bot to check if it is online
"""

from discord.ext import commands


class Testing(commands.Cog):
    """
    This class contains the commands to test the bot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Pings the bot to check if it is online")
    async def ping(self, ctx):
        """
        Function to ping the bot
        """
        await ctx.send("Pong!")


async def setup(bot):
    """
    Function to setup the testing cog
    """
    await bot.add_cog(Testing(bot))
