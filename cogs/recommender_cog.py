"""
This file contains the recommender system for the bot. It will be used to poll the users for their preferences,
and then recommend songs based on the preferences using the enhanced recommender system
"""

import discord
from discord.ext import commands
from cogs.helpers import utils
import emoji


class Recommender(commands.Cog):
    """
    This class contains the commands to poll the user,
    then recommend songs based on the user's preferences
    """

    def __init__(self, bot):
        self.bot = bot

        self.emoji_list = [
            emoji.emojize("::one::"),
            emoji.emojize("::two::"),
            emoji.emojize("::three::"),
            emoji.emojize("::four::"),
            emoji.emojize("::five::"),
            emoji.emojize("::six::"),
            emoji.emojize("::seven::"),
            emoji.emojize("::eight::"),
            emoji.emojize("::nine::"),
            emoji.emojize("::ten::"),
        ]


    @commands.command(name="poll", help="Provides the user with a poll of 10 randoms songs from the dataset to choose from. Used in conjunction witht the !recommend command")
    async def poll(self, ctx):
        """
        Function to poll the user for their preferences
        """
        
        # Get 10 random songs from the dataset, and store them in the class variable
        self.songs = utils.random_n(10).filter(["song_name", "artist_name"])

        # Create the poll message
        poll_message = "Please react to this message with your preferences:\n\n"
        for index, song in self.songs.iterrows():
            # Get the emoji icon for the index
            emoji_icon = self.emoji_list[index]

            # Add the song to the poll message
            poll_message += f"{emoji_icon} {song['song_name']} by {song['artist_name']}\n"

        # Send the poll message
        embedded_message = discord.Embed(title="Song Poll", description=poll_message, color=0x83BAE3)
        message = await ctx.send(embed=embedded_message)

        # Add the reactions to the message
        for index in range(10):
            await message.add_reaction(self.emoji_list[index])


async def setup(bot):
    """
    Function to setup the recommender cog
    """
    await bot.add_cog(Recommender(bot))
