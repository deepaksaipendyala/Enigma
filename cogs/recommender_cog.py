# cogs/recommender_cog.py
"""
This file contains the recommender system for the bot. It will be used to poll the users for their preferences,
and then recommend songs based on the preferences using the enhanced recommender system.
"""

import discord
import random
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
    This class contains the commands to poll the user,
    then recommend songs based on the user's preferences.
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
        Function to get a random color for the embed message.
        """
        return discord.Color(random.randint(0, 0xffffff))

    @commands.command(name="poll", help="Provides the user with a poll of 10 random songs from the dataset to choose from.\nUsage: !poll")
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
        self.songs = utils.random_n(10).filter(["track_name", "artist_name"]).reset_index(drop=True)

        if self.songs.empty:
            await ctx.send("❌ No songs available to poll.")
            logger.warning("poll: No songs available to display in poll.")
            return

        # Create the poll message
        poll_description = ""
        for index, song in self.songs.iterrows():
            emoji_icon = self.emoji_list[index]
            poll_description += f"{emoji_icon} **{song['track_name']}** by *{song['artist_name']}*\n"

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

    @commands.command(name="recommend", aliases=["get_songs"], help="Recommends songs based on the user's preferences.\nUsage: !recommend")
    async def recommend(self, ctx):
        """
        Function to recommend songs based on the user's preferences.
        """

        # Check if the poll command was run
        if not self.message_id:
            await ctx.send("❌ Please run the `!poll` command first to choose your preferences.")
            logger.warning("recommend: Poll has not been run yet.")
            return

        try:
            # Fetch the poll message
            poll_message = await ctx.fetch_message(self.message_id)
        except Exception as e:
            await ctx.send("❌ Unable to fetch the poll message. Please try running the `!poll` command again.")
            logger.error(f"recommend: Error fetching poll message: {e}")
            return

        # Get all reactions excluding the bot's own reactions
        reactions = [reaction for reaction in poll_message.reactions if reaction.me is False]

        if not reactions:
            await ctx.send("❌ No reactions found on the poll message.")
            logger.warning("recommend: No reactions found on poll message.")
            return

        # Collect user's selected songs based on reactions
        selected_songs = []
        for reaction in reactions:
            if reaction.count > 1:  # More than just the bot's reaction
                emoji = reaction.emoji
                if emoji in self.emoji_list:
                    index = self.emoji_list.index(emoji)
                    if index < len(self.songs):
                        song = self.songs.iloc[index]
                        selected_songs.append((song['track_name'], song['artist_name']))

        if not selected_songs:
            await ctx.send("❌ You did not select any songs. Please react to the poll message with your preferences.")
            logger.info("recommend: No songs selected by the user.")
            return

        # Send confirmation of selected songs
        confirm_message = "✅ You have selected the following song(s):\n"
        for song in selected_songs:
            confirm_message += f"**{song[0]}** by *{song[1]}*\n"

        await ctx.send(confirm_message)
        logger.info(f"recommend: Selected songs for recommendation: {selected_songs}")

        # Clear previous message references
        self.message_id = None
        self.command_msg_id = None

        # Get recommendations based on selected songs
        recommended_songs = recommend(selected_songs)

        if not recommended_songs:
            await ctx.send("❌ No recommendations found based on your preferences.")
            logger.warning("recommend: No recommendations generated.")
            return

        # Send the recommendations to the user
        recommendation_description = ""
        for idx, song in enumerate(recommended_songs, start=1):
            recommendation_description += f"**{idx}. {song[0]}** by *{song[1]}*\n"

        embed = discord.Embed(
            title="🎶 Recommendations 🎶",
            description=recommendation_description,
            color=self.random_color()
        )
        recommend_message = await ctx.send(embed=embed)

        # Ask the user if they want to add the recommended songs to the queue
        add_options = [
            "✅ Add to the end of the queue",
            "🗑️ Clear the queue and add the songs",
            "❌ Cancel"
        ]

        add_description = ""
        for option in add_options:
            add_description += f"{option}\n"

        embed = discord.Embed(
            title="Add Recommendations to Queue",
            description=add_description,
            color=self.random_color()
        )
        add_msg = await ctx.send(embed=embed)

        # Add reactions for user choices
        reaction_emojis = ["✅", "🗑️", "❌"]
        for emoji in reaction_emojis:
            await add_msg.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reaction_emojis and reaction.message.id == add_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⏰ You did not respond in time. Please run the `!recommend` command again if you wish to add songs to the queue.")
            logger.info("recommend: User did not respond to add recommendations prompt.")
            return

        if reaction.emoji == "✅":
            # Add songs to the end of the queue
            self.queue.add_to_queue(recommended_songs)
            await ctx.send("✅ Recommended songs have been added to the end of the queue.")
            logger.info("recommend: Added recommended songs to the end of the queue.")
        elif reaction.emoji == "🗑️":
            # Clear the queue and add the songs
            self.queue.clear()
            self.queue.add_to_queue(recommended_songs)
            await ctx.send("🗑️ Queue cleared and recommended songs have been added.")
            logger.info("recommend: Cleared the queue and added recommended songs.")
        elif reaction.emoji == "❌":
            # Cancel the operation
            await ctx.send("❌ Operation cancelled.")
            logger.info("recommend: User cancelled the add recommendations operation.")
        else:
            await ctx.send("❌ Invalid reaction. Please run the command again.")
            logger.warning(f"recommend: User reacted with an invalid emoji: {reaction.emoji}")

async def setup(bot):
    """
    Function to setup the recommender cog.
    """
    await bot.add_cog(Recommender(bot))
