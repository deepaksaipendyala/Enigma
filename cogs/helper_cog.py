# cogs/helper_cog.py
"""
This file contains functions that get the help string for each command and return it to the user.
"""

from discord.ext import commands
import discord
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

class Helper(commands.Cog):
    """
    Provides helper commands for the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="showCommands", aliases=["show"], help="Shows all the commands available.")
    async def show_commands(self, ctx):
        """Prints all the commands available to the user."""

        embed = discord.Embed(
            title="📜 Available Commands 📜",
            description=f"Use `!help <command>` for more information on a specific command.",
            color=discord.Color.blue()
        )

        # Organize commands by cog/category
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            if commands_list:
                command_details = ""
                for command in commands_list:
                    command_details += f"`{command.name}` - {command.help}\n"
                embed.add_field(name=cog_name, value=command_details, inline=False)

        # Add uncategorized commands if any
        uncategorized_commands = [cmd for cmd in self.bot.commands if not cmd.cog]
        if uncategorized_commands:
            command_details = ""
            for command in uncategorized_commands:
                command_details += f"`{command.name}` - {command.help}\n"
            embed.add_field(name="Uncategorized", value=command_details, inline=False)

        await ctx.send(embed=embed)
        logger.info("Displayed all available commands to the user.")

    @commands.command(name="help", help="Shows detailed help for commands or categories.")
    async def help_command(self, ctx, *, arg=None):
        """
        Provides detailed help for a specific command or category.
        """

        if arg is None:
            # Show general help
            embed = discord.Embed(
                title="📖 Help - Command Categories",
                description="Use `!help <category>` or `!help <command>` for more information.",
                color=discord.Color.green()
            )

            for cog_name, cog in self.bot.cogs.items():
                commands_list = cog.get_commands()
                if commands_list:
                    embed.add_field(name=cog_name, value=f"Contains {len(commands_list)} commands.", inline=False)

            uncategorized_commands = [cmd for cmd in self.bot.commands if not cmd.cog]
            if uncategorized_commands:
                embed.add_field(name="Uncategorized", value=f"Contains {len(uncategorized_commands)} commands.", inline=False)

            await ctx.send(embed=embed)
            logger.info("Displayed general help to the user.")
            return

        # Check if the argument matches a category (cog)
        cog = self.bot.get_cog(arg.capitalize())
        if cog:
            embed = discord.Embed(
                title=f"📂 Category: {arg.capitalize()}",
                description=f"Commands under the `{arg.capitalize()}` category:",
                color=discord.Color.orange()
            )
            for command in cog.get_commands():
                embed.add_field(name=f"!{command.name}", value=command.help, inline=False)
            await ctx.send(embed=embed)
            logger.info(f"Displayed help for category '{arg.capitalize()}' to the user.")
            return

        # Check if the argument matches a command
        command = self.bot.get_command(arg.lower())
        if command:
            embed = discord.Embed(
                title=f"🔍 Command: !{command.name}",
                description=command.help,
                color=discord.Color.purple()
            )
            embed.add_field(name="Usage", value=command.brief or "No additional usage info.", inline=False)
            await ctx.send(embed=embed)
            logger.info(f"Displayed help for command '!{command.name}' to the user.")
            return

        # If neither, inform the user
        await ctx.send(f"❌ No help available for `{arg}`. Please check the command or category name.")
        logger.warning(f"help_command: No help available for '{arg}'.")

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Helper(bot))
