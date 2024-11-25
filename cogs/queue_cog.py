# cogs/queue_cog.py
"""
A cog that handles the queue commands for the bot.
"""

import discord
from discord.ext import commands
from cogs.helpers.songs_queue import Songs_Queue
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

class Queue(commands.Cog):
    """
    This class handles generating a queue and subsequent queue commands.
    """

    def __init__(self, bot):
        self.bot = bot
        self.songs_queue = Songs_Queue()

    @commands.command(name="move", help="To move a song within the queue.\nUsage: !move <song_name> <new_position>")
    async def move(self, ctx, song_name: str, new_position: int):
        """
        Function to move a song within the queue.

        Parameters:
            song_name (str): Name of the song to move.
            new_position (int): New position in the queue (1-based index).
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        ret_val = self.songs_queue.move_song(song_name, new_position)
        if ret_val == -1:
            await ctx.send("❌ Song does not exist in the queue.")
            logger.warning(f"move: Song '{song_name}' does not exist in the queue.")
        elif ret_val == -2:
            await ctx.send("❌ Index not valid for queue.")
            logger.warning(f"move: Invalid new position '{new_position}' provided.")
        else:
            await ctx.send(f"✅ Moved **{song_name}** to position {new_position}.")
            logger.info(f"Moved '{song_name}' to position {new_position} in the queue.")

    @commands.command(name="queue", help="Show active queue of recommendations.\nUsage: !queue")
    async def songs_queue(self, ctx):
        """
        Function to display all the songs in the queue.
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        queue, index = self.songs_queue.return_queue()
        if not queue:
            await ctx.send("🎵 The queue is currently empty.")
            logger.info("songs_queue: Queue is empty.")
            return

        embed = discord.Embed(
            title="🎶 Current Song Queue 🎶",
            color=discord.Color.blue()
        )

        queue_description = ""
        already_played = []
        up_next = []

        for idx, song in enumerate(queue):
            if idx < index:
                already_played.append(f"{idx + 1}. **{song[0]}** by *{song[1]}*")
            elif idx == index:
                queue_description += f"🔊 **Now Playing:** {song[0]} by *{song[1]}*\n"
                if len(queue) > index + 1:
                    queue_description += "🎧 **Up Next:**\n"
            else:
                up_next.append(f"{idx + 1}. **{song[0]}** by *{song[1]}*")

        if already_played:
            embed.add_field(name="✅ Already Played", value="\n".join(already_played), inline=False)

        if queue_description:
            embed.add_field(name="", value=queue_description, inline=False)

        if up_next:
            embed.add_field(name="", value="\n".join(up_next), inline=False)

        await ctx.send(embed=embed)
        logger.info("songs_queue: Displayed current queue to the user.")

    @commands.command(name="shuffle", help="To shuffle songs in the queue.\nUsage: !shuffle")
    async def shuffle(self, ctx):
        """
        Function to shuffle songs in the queue.
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        self.songs_queue.shuffle_queue()
        await ctx.send("🔀 Playlist shuffled.")
        logger.info("shuffle: Queue shuffled.")

    @commands.command(name="add", aliases=["add_song"], help="To add a custom song to the queue.\nUsage: !add <song_name>")
    async def add_song(self, ctx, *, song_name: str):
        """
        Function to add a custom song to the queue.

        Parameters:
            song_name (str): Name of the song to add.
        """

        # Fetch artist name and song details from Spotify
        metadata = utils.fetch_spotify_metadata(song_name)
        if not metadata:
            await ctx.send(f"❌ Unable to find the song **{song_name}** on Spotify.")
            logger.warning(f"add_song: Song '{song_name}' not found on Spotify.")
            return

        song = (metadata['track_name'], metadata['artist'])
        self.songs_queue.add_to_queue(song)
        await ctx.send(f"✅ Added **{song[0]}** by *{song[1]}* to the queue.")
        logger.info(f"add_song: Added '{song[0]}' by '{song[1]}' to the queue.")

    @commands.command(name="remove", aliases=["remove_song"], help="To remove a song from the queue.\nUsage: !remove <song_name>")
    async def remove_song(self, ctx, *, song_name: str):
        """
        Function to remove a song from the queue.

        Parameters:
            song_name (str): Name of the song to remove.
        """

        removed = self.songs_queue.remove_from_queue(song_name)
        if removed == -1:
            await ctx.send("❌ Song does not exist in the queue.")
            logger.warning(f"remove_song: Song '{song_name}' does not exist in the queue.")
        else:
            await ctx.send(f"✅ Removed **{removed[0]}** by *{removed[1]}* from the queue.")
            logger.info(f"remove_song: Removed '{removed[0]}' by '{removed[1]}' from the queue.")

    @commands.command(name="clear", aliases=["clear_queue"], help="To clear all songs in the queue.\nUsage: !clear")
    async def clear_queue(self, ctx):
        """
        Function to clear the entire song queue.
        """
        self.songs_queue.clear()
        await ctx.send("🗑️ Queue cleared.")
        logger.info("clear_queue: Cleared the entire queue.")

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Queue(bot))
