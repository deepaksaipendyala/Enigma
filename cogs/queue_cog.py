"""
A cog that handles the queue commands for the bot.
"""

from discord.ext import commands
from helpers.songs_queue import Songs_Queue
import asyncio

class Queue(commands.Cog):
    """
    This class handles generating a queue, and subsequent queue commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.songs_queue = Songs_Queue()


    #TODO: update queue implementation
    @commands.command(name="move", help="To move a song within a queue")
    async def move(self, ctx):
        """
        Function to move a song within a queue
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if not empty_queue:
            user_message = str(ctx.message.content)
            song_name = user_message.split(" ", 1)[1].rsplit(" ", 1)[0]
            idx = user_message.rsplit(" ", 1)[1]
            ret_val = self.songs_queue.move_song(song_name, idx)
            if ret_val == -1:
                await ctx.send("Song does not exist in the queue.")
            elif ret_val == -2:
                await ctx.send("Index not valid for queue.")
            else:
                bot_message = song_name + " moved to position " + idx
                await ctx.send(bot_message)


    #TODO: update queue implementation
    @commands.command(name="queue", help="Show active queue of recommendations")
    async def songs_queue(self, ctx):
        """
        Function to display all the songs in the queue
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if not empty_queue:
            queue, index = self.songs_queue.return_queue()
            bot_message = "🎶 **Song Queue:** 🎶 "
            if index != 0:
                bot_message += "\n\nAlready Played: "
            for i in range(len(queue)):
                if i < index:
                    bot_message += "\n" + str(len(self.songs_queue.queue) - index + i) + ". " + str.title(queue[i][0])# + " by " + str.title(queue[i][1])
                elif i == index:
                    bot_message += "\n\n🔊 Currently Playing: \n" + "     " + str.title(queue[i][0])# + " by " + str.title(queue[i][1])
                    if index != len(self.songs_queue.queue) - 1: bot_message += "\n\nUp Next: "
                elif i > index:
                    bot_message += "\n" + str(i - index) + ". " + str.title(queue[i][0])# + " by " + str.title(queue[i][1])
            await ctx.send(bot_message)

    #TODO: update queue implementation
    @commands.command(name="shuffle", help="To shuffle songs in queue")
    async def shuffle(self, ctx):
        """
        Function to shuffle songs in the queue
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if not empty_queue:
            self.songs_queue.shuffle_queue()
            await ctx.send("Playlist shuffled")

    #TODO: update queue implementation
    @commands.command(name="add", aliases = ["add_song"], help="To add custom song to the queue")
    async def add_song(self, ctx):
        """
        Function to add custom song to the queue
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        self.songs_queue.add_to_queue(song_name)
        if self.songs_queue.get_len() == 1:
            ctx.command = self.bot.get_command("start")
            await self.bot.invoke(ctx)
        await ctx.send("Song added to queue")

    #TODO: update queue implementation
    @commands.command(name="remove", aliases = ["remove_song"], help="To remove a song from the queue")
    async def remove_song(self, ctx):
        """
        Function to remove a song from the queue
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        await self.songs_queue.handle_empty_queue(ctx)
        current_index = self.songs_queue._index
        result = self.songs_queue.remove_from_queue(song_name)
        if result == -1:
            await ctx.send("Song does not exist in the queue.")
        elif result == current_index:
            ctx.command = self.bot.get_command("stop")
            await self.bot.invoke(ctx)
            if self.songs_queue.get_len() != 0:
                self.songs_queue.next_song()
                ctx.command = self.bot.get_command("start")
                await self.bot.invoke(ctx)
            await ctx.send("Song removed from queue.")
        else:
            await ctx.send("Song removed from queue.")
    

    #TODO: update queue implementation
    @commands.command(name="clear", aliases = ["clear_queue"], help="To clear all songs in the queue")
    async def clear_queue(self, ctx):
        """
        Function to remove a song from the queue
        """
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            ctx.command = self.bot.get_command("stop")
            await self.bot.invoke(ctx)
        self.songs_queue._queue = []
        await ctx.send("Queue cleared.")


async def setup(bot):
    """Add the cog to the bot"""

    await bot.add_cog(Queue(bot))