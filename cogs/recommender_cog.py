# cogs/recommender_cog.py
"""
This file contains the recommender system for the bot. It polls users for their preferences
and recommends songs based on those preferences using an enhanced recommender system.
"""

import discord
import random
import shlex
import asyncio
from discord.ext import commands
from cogs.helpers import utils
from cogs.helpers.recommend_enhanced import recommend_enhanced as recommend
from cogs.helpers.songs_queue import Songs_Queue
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

class Recommender(commands.Cog):
    """
    This class contains commands to poll the user and then recommend songs based on the user's preferences.
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
            "🔟",
            "✅",
            "🗑️",
            "❌"
        ]

    def random_color(self):
        """
        Returns a random color for the embed message.
        """
        return discord.Color(random.randint(0, 0xFFFFFF))

    @commands.command(name="poll", help="Provides a poll of 10 random songs from the dataset to choose from.\nUsage: !poll")
    async def poll(self, ctx):
        """
        Function to poll the user for their song preferences.
        """

        # Delete the previous poll message and command message if they exist
        if self.message_id and self.command_msg_id:
            try:
                message = await ctx.fetch_message(self.message_id)
                await message.delete()
                command_msg = await ctx.fetch_message(self.command_msg_id)
                await command_msg.delete()
                logger.info("Deleted previous poll and command messages.")
            except Exception as e:
                logger.error(f"Error deleting previous messages: {e}")

        # Get 10 random songs from the dataset
        self.songs = utils.random_n(10).filter(["track_name", "artist"]).reset_index(drop=True)

        if self.songs.empty:
            await ctx.send("❌ No songs available to poll.")
            logger.warning("poll: No songs available to display in poll.")
            return

        # Create the poll message
        poll_description = ""
        for index, song in self.songs.iterrows():
            emoji_icon = self.emoji_list[index]
            poll_description += f"{emoji_icon} **{song['track_name']}** by *{song['artist']}*\n"

        poll_description += "\n**Please react with the corresponding emoji(s) to select your preferred songs.**"

        embed = discord.Embed(
            title="🎵 Song Poll 🎵",
            description=poll_description,
            color=self.random_color()
        )

        poll_message = await ctx.send(embed=embed)

        # Add reactions to the poll message
        for reaction in self.emoji_list[:len(self.songs)]:
            await poll_message.add_reaction(reaction)

        # Store message IDs for future reference
        self.message_id = poll_message.id
        self.command_msg_id = ctx.message.id

        logger.info("poll: Poll created and reactions added.")

    @commands.command(name="recommend", aliases=["get_songs"], help="Recommends songs based on your preferences. Must first call the !poll command.\nUsage: !recommend")
    async def recommend(self, ctx):
        """
        Function to recommend songs based on the user's preferences.
        """

        # Check if the user has run the poll command
        if not self.message_id:
            await ctx.send("❌ Please run the `!poll` command first to choose your preferences.")
            logger.warning("recommend: Poll has not been run yet.")
            return

        # Get the poll message
        try:
            message = await ctx.fetch_message(self.message_id)
        except Exception as e:
            await ctx.send("❌ Unable to fetch the poll message. Please try running the `!poll` command again.")
            logger.error(f"recommend: Error fetching poll message: {e}")
            return

        # Get the reactions
        reactions = message.reactions

        # Get the user's preferences
        preferences = []
        for reaction in reactions:
            if str(reaction.emoji) in self.emoji_list:
                # Get the users who reacted to this reaction
                users = [u async for u in reaction.users() if not u.bot]
                if ctx.author in users:
                    index = self.emoji_list.index(str(reaction.emoji))
                    if index < len(self.songs):
                        song = self.songs.iloc[index]
                        preferences.append(song)
                        logger.debug(f"recommend: User selected song '{song['track_name']}' by '{song['artist']}'.")

        # Send the user the chosen songs
        if not preferences:
            choose_message = "❌ You have not chosen any songs. Please react to the poll message with the corresponding emoji to choose a song."
            await ctx.send(choose_message)
            logger.info("recommend: No songs selected by the user.")
            return
        else:
            choose_message = "✅ You have chosen the following song(s):\n\n"
            for song in preferences:
                choose_message += f"**{song['track_name']}** by *{song['artist']}*\n"

        # Clear the message references
        self.message_id = None
        self.command_msg_id = None

        embedded_message = discord.Embed(
            title="Chosen Songs",
            description=choose_message,
            color=self.random_color()
        )
        await ctx.send(embed=embedded_message)

        # Get the user preferences as a list of tuples
        user_input = [(song["track_name"], song["artist"]) for song in preferences]

        # Get the recommendations
        await ctx.send("🔄 Generating recommendations, please wait...")
        loop = asyncio.get_event_loop()
        recommendations = await loop.run_in_executor(None, recommend, user_input)

        if not recommendations:
            await ctx.send("❌ No recommendations found based on your preferences.")
            logger.warning("recommend: No recommendations generated.")
            return

        # Send the recommendations to the user
        recommend_message = ""
        for song in recommendations:
            recommend_message += f"**{song[0]}** by *{song[1]}*\n"

        embedded_message = discord.Embed(
            title="Recommendations",
            description=recommend_message,
            color=self.random_color()
        )
        await ctx.send(embed=embedded_message)

        # Ask if the user wants to add the recommended songs to the queue
        add_message = "Would you like to add the recommended songs to the queue? React with the corresponding emoji to choose an option."
        add_options = [
            f"{self.emoji_list[0]} **Add to the end of the queue**",
            f"{self.emoji_list[1]} **Clear the queue and add the songs**",
            f"{self.emoji_list[2]} **Cancel**"
        ]
        add_message += "\n\n" + "\n".join(add_options)

        embedded_message = discord.Embed(
            title="Add Recommendations to Queue",
            description=add_message,
            color=self.random_color()
        )
        message = await ctx.send(embed=embedded_message)

        # Add the reactions to the message
        for emoji in self.emoji_list[:3]:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in self.emoji_list[:3] and reaction.message.id == message.id

        # Wait for the user's response
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            if reaction.emoji == self.emoji_list[0]:
                # Add the songs to the end of the queue
                await ctx.send("✅ Adding the songs to the end of the queue.")
                self.queue.add_to_queue(recommendations)
                await ctx.send(f"Songs added to the queue. Start playback with the `!start` command.")
                logger.info("recommend: Added recommended songs to the end of the queue.")
            elif reaction.emoji == self.emoji_list[1]:
                # Clear the queue and add the songs
                await ctx.send("🗑️ Clearing the queue and adding the songs.")
                self.queue.clear()
                self.queue.add_to_queue(recommendations)
                await ctx.send(f"Songs added to the queue. Start playback with the `!start` command.")
                logger.info("recommend: Cleared the queue and added recommended songs.")
            elif reaction.emoji == self.emoji_list[2]:
                # Cancel the operation
                await ctx.send("❌ Operation cancelled.")
                logger.info("recommend: User cancelled the add recommendations operation.")
            else:
                await ctx.send("❌ Invalid reaction. Please run the command again.")
                logger.warning(f"recommend: User reacted with an invalid emoji: {reaction.emoji}")
        except asyncio.TimeoutError:
            await ctx.send("⏰ You did not respond in time. Please run the command again.")
            logger.info("recommend: User did not respond to add recommendations prompt.")
            return

    @commands.command(name="myrecommend", help="Adds up to 10 user-specified songs to the queue.\nUsage: !myrecommend <song1> [<song2> ...]")
    async def myrecommend(self, ctx, *, song_names: str):
        """
        Function to add user-specified songs to the queue.

        Parameters:
            song_names (str): A string containing up to 10 song names.
        """
        # Split song_names using shlex.split to handle quoted strings
        song_list = shlex.split(song_names)
        if not song_list:
            await ctx.send("❌ Please provide at least one song name.")
            logger.warning("myrecommend: No song names provided.")
            return

        if len(song_list) > 10:
            await ctx.send("❌ You can specify up to 10 songs only.")
            logger.warning("myrecommend: More than 10 song names provided.")
            return

        await ctx.send("🔄 Adding your songs to the queue, please wait...")

        added_songs = []

        # Use asyncio.gather to fetch metadata concurrently
        tasks = [self.fetch_and_add_song(song_name) for song_name in song_list]
        results = await asyncio.gather(*tasks)

        for song_name, result in zip(song_list, results):
            if result:
                added_songs.append(result)
            else:
                await ctx.send(f"⚠️ Could not find '{song_name}' on Spotify.")
                logger.warning(f"myrecommend: Song '{song_name}' not found on Spotify.")

        if added_songs:
            message = "✅ Added the following songs to the queue:\n"
            for song in added_songs:
                message += f"**{song[0]}** by *{song[1]}*\n"
            await ctx.send(message)
            logger.info(f"myrecommend: Added {len(added_songs)} songs to the queue.")
        else:
            await ctx.send("❌ No songs were added to the queue.")
            logger.warning("myrecommend: No songs were added to the queue.")

    async def fetch_and_add_song(self, song_name):
        """
        Asynchronously fetches song metadata and adds it to the queue.

        Parameters:
            song_name (str): Name of the song.

        Returns:
            tuple or None: Song tuple if added, None otherwise.
        """
        # Fetch metadata in a separate thread
        loop = asyncio.get_event_loop()
        metadata = await loop.run_in_executor(None, utils.fetch_spotify_metadata, song_name)
        if metadata:
            song_tuple = (metadata['track_name'], metadata['artist'])
            self.queue.add_to_queue(song_tuple)
            logger.info(f"myrecommend: Added '{song_tuple[0]}' by '{song_tuple[1]}' to the queue.")
            return song_tuple
        else:
            logger.warning(f"myrecommend: Song '{song_name}' not found on Spotify.")
            return None


async def setup(bot):
    """
    Function to setup the recommender cog.
    """
    await bot.add_cog(Recommender(bot))
