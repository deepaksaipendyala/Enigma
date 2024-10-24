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
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟"
        ]


    @commands.command(name="poll", help="Provides the user with a poll of 10 randoms songs from the dataset to choose from. Used in conjunction witht the !recommend command")
    async def poll(self, ctx):
        """
        Function to poll the user for their preferences
        """
        
        # Get 10 random songs from the dataset, and store them in the class variable
        self.songs = utils.random_n(10).filter(["track_name", "artist_name"]).reset_index(drop=True)

        # Create the poll message
        poll_message = "Please react to this message with your preferences:\n\n"
        for index, song in self.songs.iterrows():
            # Get the emoji icon for the index
            emoji_icon = self.emoji_list[index]

            # Add the song to the poll message
            poll_message += f"{emoji_icon} {song['track_name']} by {song['artist_name']}\n"

        # Add instructions to the poll message
        poll_message += "\n*If you don't like any of the songs, you may run the command again to get new songs*\n"
        poll_message += "\n**Once you have chosen your songs, run the !recommend command to get your recommendations**"

        ads = [""]
        # Send the poll message
        embedded_message = discord.Embed(title="Song Poll", description = poll_message + ads[0], color=0xab0505)
        message = await ctx.send(embed=embedded_message)

        # Add the reactions to the message
        for reaction in self.emoji_list[:len(self.emoji_list)]:
            await message.add_reaction(reaction)

        # Store the message id
        self.message_id = message.id

        # await ctx.send("Choose a song(s) by reacting with the corresponding emoji, or if you don't like any of the songs, run the command again.")
        # await ctx.send("Once you have chosen your songs, run the !recommend command to get your recommendations")

    
    @commands.command(name="recommend", help="Recommends songs based on the user's preferences. Must first call the !poll command")
    async def recommend(self, ctx):
        """
        Function to recommend songs based on the user's preferences
        """

        # Get the message
        message = await ctx.fetch_message(self.message_id)

        # Get the reactions
        reactions = message.reactions

        # Get the user's preferences
        preferences = []
        for reaction in reactions:
            if reaction.count > 1:
                # if there is more than one reaction on a reaction, then the user has reacted to it, so add the corresponding song to the preferences
                index = self.emoji_list.index(reaction.emoji)
                preferences.append(self.songs.iloc[index])

        # Send the user the chosen songs
        choose_message = "You have chosen the following songs:\n\n"
        if not preferences:
            choose_message = "You have not chosen any songs. Please react to the poll message with the corresponding emoji to choose a song."
        else:
            for song in preferences:
                choose_message += f"***{song['track_name']}* by *{song['artist_name']}***\n"

        embedded_message = discord.Embed(title="Chosen Songs", description = choose_message, color=0x0dd649)
        await ctx.send(embed=embedded_message)


async def setup(bot):
    """
    Function to setup the recommender cog
    """
    await bot.add_cog(Recommender(bot))
