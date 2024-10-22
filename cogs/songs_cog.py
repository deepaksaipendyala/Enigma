"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""

import discord
from cogs.helpers.get_all import *
from dotenv import load_dotenv
from discord.ext import commands
from cogs.helpers.utils import searchSong, random_25
from cogs.helpers.songs_queue import Songs_Queue
import yt_dlp as youtube_dl


FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": [
        "ffmpeg",
        "-i",
        "./assets/sample.mp4",
        "-vn",
        "-f",
        "mp3",
        "./assets/sample.mp3",
    ],
}
YDL_OPTIONS = {"format": "bestaudio/best", "noplaylist": "True"}


def get_audio_sorce(url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_flat": "in_playlist",
        "noplaylist": True,
        "no_warnings": True,
        "cookies": "../cookies.txt",
        "outtmpl": "downloaded_music/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]
        return discord.FFmpegOpusAudio(audio_url, **FFMPEG_OPTIONS)


class Songs(commands.Cog):
    """
    Cog for bot that handles all commands related to songs
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", help="To join the voice channel")
    async def join(self, ctx, channel: str = commands.parameter(description="The voice channel to join (optional)", default=None)):
        """
        Function for joining the voice channel

        Parameters:
            channel (discord.VoiceChannel): The voice channel to join
        """

        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("No channel to join. Please specify a channel")
                return

        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"Successfully joined {channel.name} ({channel.id})")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx):
        """
        Function for handling resume capability
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play command"
            )

    @commands.command(
        name="play_song",
        help="To play user defined song, does not need to be in the database.",
    )
    async def play_custom(self, ctx):
        """
        Function for playing a custom song
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        await self.play_song(song_name, ctx)

    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx):
        """
        Function to stop playing the music
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    async def play_song(self, song_name, ctx):
        """
        Helper function for playing song on the voice channel

        Parameters:
            song_name (str): The name of the song to play
        """

        # Get the song URL
        url = searchSong(song_name)
        print(url)

        # Check if bot is connected to a voice channel
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to a voice channel")
            return

        # Check if the bot is already playing a song, and stop it if it is
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        # Get and play the audio source
        audio_source = get_audio_sorce(url)
        ctx.voice_client.play(audio_source)
        await ctx.send(f"Now playing: {url}")

    async def handle_empty_queue(self, ctx):
        """
        Helper function to handle empty song queue
        """
        try:
            songs_queue
        except NameError:
            await ctx.send(
                "No recommendations present. First generate recommendations using /poll"
            )
            return True
        if songs_queue.get_len() == 0:
            await ctx.send(
                "No recommendations present. First generate recommendations using /poll"
            )
            return True
        return False

    @commands.command(name="next_song", help="To play next song in queue")
    async def next_song(self, ctx):
        """
        Function to play the next song in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.next_song(), ctx)

    @commands.command(name="prev_song", help="To play prev song in queue")
    async def play(self, ctx):
        """
        Function to play the previous song in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.prev_song(), ctx)

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

    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx):
        """
        Function to pause the music that is playing
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(
        name="poll_old",
        help="Generate a poll to create some recommendations. This is the old version",
    )
    async def poll(self, ctx):
        """
        Function to generate poll for playing the recommendations
        """

        reactions = ["👍", "👎"]
        selected_songs = []
        count = 0
        bot_message = "Select song preferences by reaction '👍' or '👎' to the choices. \nSelect 3 songs"
        await ctx.send(bot_message)
        ten_random_songs = random_25()
        for ele in zip(ten_random_songs["track_name"], ten_random_songs["artist"]):
            bot_message = str(ele[0]) + " By " + str(ele[1])
            description = []
            poll_embed = discord.Embed(
                title=bot_message, color=0x31FF00, description="".join(description)
            )
            react_message = await ctx.send(embed=poll_embed)
            for reaction in reactions[: len(reactions)]:
                await react_message.add_reaction(reaction)
            res, user = await self.bot.wait_for("reaction_add")
            if res.emoji == "👍":
                selected_songs.append(str(ele[0]))
                count += 1
            if count == 3:
                bot_message = "Selected songs are : " + " , ".join(selected_songs)
                await ctx.send(bot_message)
                break
        global songs_queue
        recommended_songs = recommend(selected_songs)
        songs_queue = Songs_Queue(recommended_songs)
        await self.play_song(songs_queue.next_song(), ctx)

    @commands.command(name="queue", help="Show active queue of recommendations")
    async def queue(self, ctx):
        """
        Function to display all the songs in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            queue, index = songs_queue.return_queue()
            bot_message = "🎶 **Song Queue:** 🎶 \n"
            if index != 0:
                bot_message += "\nAlready Played: "
            for i in range(len(queue)):
                if i < index:
                    bot_message += "\n" + "     " + str.title(queue[i])
                elif i == index:
                    bot_message += "\n\n🔊 Currently Playing: \n" + "     " + str.title(queue[i])
                    bot_message += "\n\nIn Queue: "
                elif i > index:
                    bot_message += "\n" + str(i - index) + ". " + str.title(queue[i])
            await ctx.send(bot_message)

    @commands.command(name="shuffle", help="To shuffle songs in queue")
    async def shuffle(self, ctx):
        """
        Function to shuffle songs in the queue
        """

        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            songs_queue.shuffle_queue()
            await ctx.send("Playlist shuffled")

    @commands.command(name="add_song", help="To add custom song to the queue")
    async def add_song(self, ctx):
        """
        Function to add custom song to the queue
        """

        user_message = str(ctx.message.content)
        song_name = user_message.split(" ", 1)[1]
        songs_queue.add_to_queue(song_name)
        await ctx.send("Song added to queue")


async def setup(client: discord.Client):
    """
    Function to add the cog to the bot

    Parameters:
        client (discord.Client): The bot client
    """

    await client.add_cog(Songs(client))
