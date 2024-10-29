"""
This file contains the recommender system for the bot. It will be used to poll the users for their preferences,
and then recommend songs based on the preferences using the enhanced recommender system
"""

import discord
import random
import asyncio
from discord.ext import commands
from helpers import utils
from helpers.recommend_enhanced import recommend_enhanced as recommend
from helpers.songs_queue import Songs_Queue


class Recommender(commands.Cog):
    """
    This class contains the commands to poll the user,
    then recommend songs based on the user's preferences
    """

    def __init__(self, bot):
        self.bot = bot
        self.message_id = None
        self.command_msg_id = None

        # Get the queue instance
        self.queue = Songs_Queue()

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

    def random_color(self):
        """
        Function to get a random color for the embed message
        """
        return discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @commands.command(name="poll", help="Provides the user with a poll of 10 randoms songs from the dataset to choose from. Used in conjunction witht the !recommend command")
    async def poll(self, ctx):
        """
        Function to poll the user for their preferences
        """

        # Delete the previous poll message and command message if it exists
        if self.message_id and self.command_msg_id:
            try:
                message = await ctx.fetch_message(self.message_id)
                await message.delete()
                command_msg = await ctx.fetch_message(self.command_msg_id)
                await command_msg.delete()
            except Exception as e:
                print(e)

        # Get 10 random songs from the dataset, and store them in the class variable
        self.songs = utils.random_n(10).filter(
            ["track_name", "artist_name"]).reset_index(drop=True)

        # Create the poll message
        poll_message = "Please react to this message with your preferences:\n\n"
        for index, song in self.songs.iterrows():
            # Get the emoji icon for the index
            emoji_icon = self.emoji_list[index]

            # Add the song to the poll message
            poll_message += f"{emoji_icon} **{song['track_name']} *by* {song['artist_name']}**\n"

        # Add instructions to the poll message
        poll_message += "\n*If you don't like any of the songs, you may run the command again to get new songs*\n"
        poll_message += "\n**Once you have chosen your songs, run the !recommend command to get your recommendations**"

        ads = [""]
        # Send the poll message
        embedded_message = discord.Embed(
            title="Song Poll", description=poll_message + ads[0], color=self.random_color())
        message = await ctx.send(embed=embedded_message)

        # Add the reactions to the message
        for reaction in self.emoji_list[:len(self.emoji_list)]:
            await message.add_reaction(reaction)

        # Store the interaction
        self.message_id = message.id
        self.command_msg_id = ctx.message.id

        # await ctx.send("Choose a song(s) by reacting with the corresponding emoji, or if you don't like any of the songs, run the command again.")
        # await ctx.send("Once you have chosen your songs, run the !recommend command to get your recommendations")

    @commands.command(name="recommend", aliases=["get_songs"], help="Recommends songs based on the user's preferences. Must first call the !poll command")
    async def recommend(self, ctx):
        """
        Function to recommend songs based on the user's preferences
        """

        # Check if the user has run the poll command
        if not self.message_id:
            await ctx.send("Please run the !poll command first to choose your preferences.")
            return

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
                choose_message += f"**{song['track_name']} *by* {song['artist_name']}**\n"

        # Clear the message reference
        self.message_id = None
        self.command_msg_id = None

        embedded_message = discord.Embed(
            title="Chosen Songs", description=choose_message, color=self.random_color())
        await ctx.send(embed=embedded_message)

        # Get the user preferences as a list of tuples
        user_input = [(song["track_name"], song["artist_name"])
                      for song in preferences]

        # Get the recommendations
        recommendations = recommend(user_input)

        # Send the recommendations to the user
        recommend_message = "Here are some songs you may like based on your preferences:\n\n"
        for song, artist in recommendations:
            recommend_message += f"**{song} *by* {artist}**\n"

        embedded_message = discord.Embed(
            title="Recommendations", description=recommend_message, color=self.random_color())
        await ctx.send(embed=embedded_message)

        # ask if the user wants to add the recommended songs to the queue
        add_message = "Would you like to add the recommended songs to the queue? React with the corresponding emoji to add the songs to the end of the queue, clear the queue and add the songs, or cancel the operation."

        add_message += f"\n\n{self.emoji_list[0]} **Add to the end of the queue**"
        add_message += f"\n{self.emoji_list[1]} **Clear the queue and add the songs**"
        add_message += f"\n{self.emoji_list[2]} **Cancel**"

        embedded_message = discord.Embed(
            title="Add Recommendations to Queue", description=add_message, color=self.random_color())
        message = await ctx.send(embed=embedded_message)

        # Add the reactions to the message
        for reaction in self.emoji_list[:3]:
            await message.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in self.emoji_list[:3]
        # wait for the user's response
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)

            if reaction.emoji == self.emoji_list[0]:
                # Add the songs to the end of the queue
                await ctx.send("Adding the songs to the end of the queue.")
                self.queue.add_to_queue(recommendations)
                await ctx.send(f"Songs added to the queue. Current queue: {self.queue.queue}\nStart playback with the !start command.")
            elif reaction.emoji == self.emoji_list[1]:
                # Clear the queue and add the songs
                await ctx.send("Clearing the queue and adding the songs.")
                self.queue.clear()
                self.queue.add_to_queue(recommendations)
                await ctx.send(f"Songs added to the queue. Current queue: {self.queue.queue}\nStart playback with the !start command.")
            elif reaction.emoji == self.emoji_list[2]:
                # Cancel the operation
                await ctx.send("Operation cancelled.")
            else:
                await ctx.send("Invalid reaction. Please run the command again.")
        except asyncio.TimeoutError:
            await ctx.send("You did not respond in time. Please run the command again.")
            return


async def setup(bot):
    """
    Function to setup the recommender cog
    """
    await bot.add_cog(Recommender(bot))
