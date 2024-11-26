"""
A cog that handles queue commands for the bot.
"""

from discord.ext import commands
from cogs.helpers.songs_queue import Songs_Queue
import logging
import discord

# Initialize Logger
logger = logging.getLogger(__name__)


class Queue(commands.Cog):
    """
    Cog for managing the song queue.
    """

    def __init__(self, bot):
        self.bot = bot
        self.songs_queue = Songs_Queue()

    @commands.command(name="queue", help="Show active queue of songs.\nUsage: !queue")
    async def songs_queue(self, ctx):
        """
        Display all songs in the queue with sections:
        Already Played, Now Playing, and Up Next.
        """
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        queue, current_index = self.songs_queue.return_queue()
        if not queue:
            await ctx.send("🎵 The queue is currently empty.")
            logger.info("songs_queue: Queue is empty.")
            return

        embed = discord.Embed(
            title="🎶 Current Song Queue 🎶",
            color=discord.Color.blue()
        )

        already_played = []
        now_playing = ""
        up_next = []

        for idx, song in enumerate(queue):
            track_name = song[0]      # track_name is the first element
            artist_name = song[1]     # artist_name is the second element
            source = song[2]          # source is the third element

            # Use title if available, else use track_name
            title = track_name

            if idx < current_index:
                already_played.append(f"{idx + 1}. **{title}** by *{artist_name}*")
            elif idx == current_index:
                now_playing = f"🔊 **Now Playing:** {title} by *{artist_name}*"
            else:
                up_next.append(f"{idx + 1}. **{title}** by *{artist_name}*")

        if already_played:
            embed.add_field(
                name="✅ Already Played",
                value="\n".join(already_played),
                inline=False
            )

        if now_playing:
            embed.add_field(
                name="",
                value=now_playing,
                inline=False
            )

        if up_next:
            embed.add_field(
                name="🎧 Up Next",
                value="\n".join(up_next),
                inline=False
            )

        await ctx.send(embed=embed)
        logger.info("songs_queue: Displayed current queue to the user.")

    @commands.command(name="clear", help="Clear all songs in the queue.\nUsage: !clear")
    async def clear_queue(self, ctx):
        """
        Clear the song queue.
        """
        self.songs_queue.clear()
        await ctx.send("🗑️ Queue cleared.")
        logger.info("clear_queue: Cleared the entire queue.")

    @commands.command(name="remove", help="Remove a song from the queue by its index.\nUsage: !remove <index>")
    async def remove_song(self, ctx, index: int):
        """
        Remove a song from the queue by its index.

        Parameters:
            index (int): 1-based index of the song to remove.
        """
        queue, current_index = self.songs_queue.return_queue()
        if index < 1 or index > len(queue):
            await ctx.send("❌ Invalid index provided.")
            logger.warning(f"remove_song: Invalid index '{index}'.")
            return

        removed_song = self.songs_queue.remove_from_queue_by_index(index - 1)
        if removed_song == -1:
            await ctx.send("❌ Unable to remove the song. Invalid index.")
            logger.error(f"remove_song: Failed to remove song at index '{index - 1}'.")
            return

        track_name = removed_song[0]
        artist_name = removed_song[1]
        await ctx.send(f"✅ Removed **{track_name}** by *{artist_name}* from the queue.")
        logger.info(f"remove_song: Removed '{track_name}' by '{artist_name}' from the queue.")

    @commands.command(name="move", help="Move a song within the queue by its indices.\nUsage: !move <current_index> <new_index>")
    async def move_song(self, ctx, current_index: int, new_index: int):
        """
        Move a song within the queue from current_index to new_index.

        Parameters:
            current_index (int): Current 1-based index of the song.
            new_index (int): New 1-based index where the song should be moved.
        """
        queue, _ = self.songs_queue.return_queue()
        if (current_index < 1 or current_index > len(queue)) or (new_index < 1 or new_index > len(queue)):
            await ctx.send("❌ Invalid indices provided.")
            logger.warning(f"move_song: Invalid indices '{current_index}' or '{new_index}'.")
            return

        new_idx_zero = new_index - 1
        current_idx_zero = current_index - 1

        result = self.songs_queue.move_song_by_index(current_idx_zero, new_idx_zero)
        if result == -1:
            await ctx.send("❌ Unable to move the song. Please check the indices.")
            logger.error(f"move_song: Failed to move song from '{current_index}' to '{new_index}'.")
            return

        await ctx.send(f"✅ Moved song from position {current_index} to {new_index}.")
        logger.info(f"move_song: Moved song from position {current_index} to {new_index}.")

    @commands.command(name="shuffle", help="Shuffle the songs in the queue.\nUsage: !shuffle")
    async def shuffle_queue(self, ctx):
        """
        Shuffle songs in the queue.
        """
        self.songs_queue.shuffle_queue()
        await ctx.send("🔀 Playlist shuffled.")
        logger.info("shuffle_queue: Queue shuffled.")


async def setup(bot):
    """
    Add the cog to the bot.

    Parameters:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(Queue(bot))
