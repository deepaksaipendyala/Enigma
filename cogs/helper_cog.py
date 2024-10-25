"""
This file contains some functions that get the help string for each command, and return it to the user
"""

from discord.ext import commands


class Helper(commands.Cog):
    """
    Get the help strings for each command, and reply to the user
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="showCommands", aliases=["show"], help="Shows all the commands available")
    async def show_commands(self, ctx):
        """Prints all the commands available to the user"""

        # Get all the commands
        all_commands = []

        for cog_name, cog in self.bot.cogs.items():
            for command in cog.get_commands():
                all_commands.append(command.name)

        # Print all the commands
        await ctx.send(
            f"```To run any of the following commands, type: {self.bot.command_prefix}command_name\n" 
            "To get help on a specific command, type: !help command_name```"
        )

        await ctx.send(f"```All commands:\n\n{', '.join(all_commands)}```")


async def setup(bot):
    """Add the file to the bot"""
    await bot.add_cog(Helper(bot))
