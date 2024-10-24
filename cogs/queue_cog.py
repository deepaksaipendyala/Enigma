"""
A cog that handles the queue commands for the bot.
"""

import discord
from discord.ext import commands
from cogs.helpers.songs_queue import Songs_Queue
import asyncio

class Queue(commands.Cog):
    """
    This class handles generating a queue, and subsequent queue commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.queue = Songs_Queue()


        #TODO: update queue implementation
    @commands.command(name="skip", aliases=["next, next_song"], help="To play next song in queue")
    async def next_song(self, ctx):
        """
        Function to play the next song in the queue
        """
        
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.next_song(), ctx)


    #TODO: update queue implementation
    @commands.command(name="prev", aliases=["prev_song"], help="To play previous song in queue")
    async def play(self, ctx):
        """
        Function to play the previous song in the queue
        """
        
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.prev_song(), ctx)


    #TODO: update queue implementation
    @commands.command(name="move", help="To move a song within a queue")
    async def move(self, ctx):
        """
        Function to move a song within a queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            user_message = str(ctx.message.content)
            song_name = user_message.split(" ", 1)[1].rsplit(" ", 1)[0]
            idx = user_message.rsplit(" ", 1)[1]
            ret_val = songs_queue.move_song(song_name, idx)
            if ret_val == -1:
                await ctx.send("Song does not exist in the queue.")
            elif ret_val == -2:
                await ctx.send("Index not valid for queue.")
            else:
                bot_message = song_name + " moved to position " + idx
                await ctx.send(bot_message)

    
    #TODO: update queue implementation
    @commands.command(name="replay", help="This command replays the current song")
    async def replay(self, ctx):
        """
        Function to restart the current song in queue
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        await self.play_song(songs_queue.queue[songs_queue._index], ctx)
        

    

    #TODO: update queue implementation
    @commands.command(name="queue", help="Show active queue of recommendations")
    async def queue(self, ctx):
        """
        Function to display all the songs in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            queue, index = songs_queue.return_queue()
            bot_message = "🎶 **Song Queue:** 🎶 "
            if index != 0:
                bot_message += "\n\nAlready Played: "
            for i in range(len(queue)):
                if i < index:
                    bot_message += "\n" + str(len(songs_queue.queue) - index + i) + ". " + str.title(queue[i])
                elif i == index:
                    bot_message += "\n\n🔊 Currently Playing: \n" + "     " + str.title(queue[i])
                    if index != len(songs_queue.queue) - 1: bot_message += "\n\nUp Next: "
                elif i > index:
                    bot_message += "\n" + str(i - index) + ". " + str.title(queue[i])
            await ctx.send(bot_message)

    #TODO: update queue implementation
    @commands.command(name="shuffle", help="To shuffle songs in queue")
    async def shuffle(self, ctx):
        """
        Function to shuffle songs in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            songs_queue.shuffle_queue()
            await ctx.send("Playlist shuffled")

    #TODO: update queue implementation
    @commands.command(name="add", aliases = ["add_song"], help="To add custom song to the queue")
    async def add_song(self, ctx):
        """
        Function to add custom song to the queue
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        if 'songs_queue' not in globals():
            global songs_queue
            songs_queue = Songs_Queue([song_name])
            await self.play_song(songs_queue.queue[songs_queue._index], ctx)
        else:
            songs_queue.add_to_queue(song_name)
        await ctx.send("Song added to queue")

    #TODO: update queue implementation
    @commands.command(name="remove", aliases = ["remove_song"], help="To remove a song from the queue")
    async def remove_song(self, ctx):
        """
        Function to remove a song from the queue
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        await self.handle_empty_queue(ctx)
        current_index = songs_queue._index
        result = songs_queue.remove_from_queue(song_name)
        if result == -1:
            await ctx.send("Song does not exist in the queue.")
        elif result == current_index:
            await self.stop(ctx)
            if songs_queue.get_len() != 0:
                self.handle_play_next(ctx)
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
            await self.stop(ctx)
        songs_queue = None
        await ctx.send("Queue cleared.")


async def setup(bot):
    """Add the cog to the bot"""

    await bot.add_cog(Queue(bot))