# cogs/songs_cog.py
"""
This file is responsible for all bot commands regarding songs such as /poll for generating recommendations,
/next_song for playing next song, and so on.
"""

import asyncio
import discord
from discord.ext import commands
from cogs.helpers.get_all import *
from cogs.helpers.utils import searchSong
from cogs.helpers.songs_queue import Songs_Queue
import yt_dlp as youtube_dl
import logging
from typing import Union
from discord import PCMVolumeTransformer
from cogs.helpers.utils import fetch_spotify_metadata

# Initialize Logger
logger = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-thread_queue_size 512 '
    ),
    'options': (
        '-vn '
        '-ar 48000 '
        '-ac 2 '
        '-b:a 160k '
        '-bufsize 160k '
    )
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ytdl = youtube_dl.YoutubeDL(YDL_OPTIONS)

async def get_audio_source(url: str, song_name: str, artist: str, *, loop=None, stream=False) -> Union[PCMVolumeTransformer, dict]:
    """
    Asynchronously retrieves the audio source from YouTube.

    Parameters:
        url (str): YouTube URL of the song.
        song_name (str): Name of the song.
        artist (str): Name of the artist.

    Returns:
        Tuple[PCMVolumeTransformer, dict]: Audio source and video data.
    """
    loop = loop or asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    except Exception as e:
        logger.error(f"get_audio_source: Error extracting info from {url} - {e}")
        return None

    if data is None:
        logger.error(f"get_audio_source: No data retrieved from {url}.")
        return None

    if "entries" in data:
        data = data["entries"][0]

    filename = data["url"] if stream else ytdl.prepare_filename(data)
    logger.info(f"Fetching audio source for {data['title']} from URL: {url}")

    try:
        audio_source = discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS)
        # Wrap with PCMVolumeTransformer for volume control
        volume = 1.0  # Default volume at 100%
        audio_source = PCMVolumeTransformer(audio_source, volume=volume)
    except Exception as e:
        logger.error(f"get_audio_source: Error creating PCMVolumeTransformer - {e}")
        return None

    return (audio_source, data)

class Songs(commands.Cog):
    """
    Cog for the bot that handles all commands related to songs.
    """

    def __init__(self, bot):
        self.bot = bot
        self.manually_stopped = False
        # Initialize the songs queue
        self.songs_queue = Songs_Queue()

    # -----------Helper Functions-----------#

    def handle_play_next(self, ctx):
        if not self.manually_stopped and not ctx.voice_client.is_playing():
            asyncio.run_coroutine_threadsafe(self.play_song(
                self.songs_queue.next_song(), ctx), self.bot.loop)

    async def play_song(self, song_tuple: Union[tuple, int], ctx):
        """
        Helper function for playing song on the voice channel.

        Parameters:
            song_tuple (tuple or int): The song to play as (song_name, artist) or an error code.
            ctx: The context from Discord.
        """

        logger.debug(f"play_song: Received song_tuple: {song_tuple}, type: {type(song_tuple)}")

        if isinstance(song_tuple, int):
            await ctx.send("❌ Unable to retrieve the next song.")
            logger.error(f"play_song: Received error code {song_tuple}.")
            return

        if not isinstance(song_tuple, tuple) or len(song_tuple) != 2:
            await ctx.send("❌ Invalid song format.")
            logger.error("play_song: Invalid song format received.")
            return

        song_name, artist = song_tuple
        logger.debug(f"play_song: Playing '{song_name}' by '{artist}'.")

        url = searchSong(song_name, artist)

        if not url:
            await ctx.send(f"❌ Unable to find a YouTube link for **{song_name}** by *{artist}*.")
            logger.warning(f"play_song: No YouTube URL found for '{song_name}' by '{artist}'.")
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            await ctx.send("❌ Bot is not connected to a voice channel.")
            logger.warning("play_song: Bot is not connected to any voice channel.")
            return

        # Stop current playback if any
        if voice_client.is_playing():
            self.manually_stopped = True
            voice_client.stop()
            logger.info("play_song: Stopped current playback.")

        # Fetch and play the audio source
        try:
            async with ctx.typing():
                audio_data = await get_audio_source(url, song_name, artist, loop=self.bot.loop, stream=True)
                if audio_data is None:
                    await ctx.send("❌ Failed to retrieve audio source.")
                    logger.error("play_song: Failed to retrieve audio source.")
                    return
                player, data = audio_data
                voice_client.play(player, after=lambda e: logger.error(f"Playback error: {e}") if e else self.handle_play_next(ctx))
                logger.info(f"play_song: Playing '{data['title']}' by '{artist}'.")
        except Exception as e:
            await ctx.send("❌ An error occurred while trying to play the song.")
            logger.error(f"play_song: Exception occurred - {e}")
            return

        await ctx.send(f"🎶 Now playing: **{song_name}** by *{artist}*")
        self.manually_stopped = False

    # -----------Commands-----------#

    @commands.command(name="join", help="To join the voice channel.\nUsage: !join <channel_name> (optional)")
    async def join(self, ctx, channel_name: str = None):
        """
        Function for joining the voice channel.

        Parameters:
            channel_name (str): The voice channel to join (optional). If not provided, joins the author's current channel.
        """

        if channel_name is None:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("❌ You are not connected to a voice channel.")
                logger.warning("join: Author is not connected to any voice channel.")
                return
        else:
            channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
            if not channel:
                await ctx.send(f"❌ Voice channel '{channel_name}' not found.")
                logger.warning(f"join: Voice channel '{channel_name}' not found.")
                return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            if voice_client.channel == channel:
                await ctx.send(f"✅ Already connected to '{channel.name}'.")
                logger.info(f"join: Already connected to '{channel.name}'.")
                return
            else:
                await voice_client.move_to(channel)
                await ctx.send(f"✅ Moved to voice channel: '{channel.name}'.")
                logger.info(f"join: Moved to voice channel '{channel.name}'.")
                return
        else:
            try:
                await channel.connect()
                await ctx.send(f"✅ Connected to voice channel: '{channel.name}'.")
                logger.info(f"join: Connected to voice channel '{channel.name}'.")
            except Exception as e:
                await ctx.send(f"❌ Error connecting to voice channel: {e}")
                logger.error(f"join: Error connecting to voice channel '{channel.name}': {e}")

    @commands.command(name="resume", help="Resumes the paused song.\nUsage: !resume")
    async def resume(self, ctx):
        """
        Function to resume the paused music.
        """

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("▶️ Resumed the song.")
            logger.info("resume: Resumed the song.")
        else:
            await ctx.send("❌ The bot is not paused or not playing anything.")
            logger.warning("resume: Bot is not paused or not playing.")

    @commands.command(name="start", help="Starts playing the current song in the queue.\nUsage: !start")
    async def start(self, ctx):
        """
        Function for starting the song.
        """

        if self.songs_queue.get_len() == 0:
            await ctx.send("❌ No songs in the queue. Please add songs to the queue.")
            logger.warning("start: No songs in the queue to play.")
            return

        current_song = self.songs_queue.current_song()
        if isinstance(current_song, int):
            await ctx.send("❌ Unable to retrieve the current song.")
            logger.error(f"start: Received error code {current_song}.")
            return

        await self.play_song(current_song, ctx)
        logger.info("start: Started playing the current song.")

    @commands.command(name="play", aliases=["play_song"], help="To play a song.\nUsage: !play <song_name>")
    async def play_custom(self, ctx, *, song_name: str):
        """
        Function for playing a song. It fetches artist details from Spotify.

        Parameters:
            song_name (str): Name of the song to play.
        """

        try:
            if not song_name:
                await ctx.send("❌ Please provide the song name.")
                logger.warning("play_custom: Missing song name.")
                return

            # Fetch artist name and song details from Spotify
            metadata = fetch_spotify_metadata(song_name)
            if not metadata:
                await ctx.send(f"❌ Unable to find the song **{song_name}** on Spotify.")
                logger.warning(f"play_custom: Song '{song_name}' not found on Spotify.")
                return

            song = (metadata['track_name'], metadata['artist'])

            self.songs_queue.clear()
            self.songs_queue.add_to_queue(song)

            logger.info(f"play_custom: Playing song '{song[0]}' by '{song[1]}'.")
            logger.debug(f"play_custom: Current queue: {self.songs_queue.queue}")
            current_song = self.songs_queue.current_song()
            logger.debug(f"play_custom: Current song retrieved: {current_song}")
            await self.play_song(current_song, ctx)
        except Exception as e:
            await ctx.send("❌ An unexpected error occurred while trying to play the song.")
            logger.error(f"play_custom: Exception occurred - {e}")

    @commands.command(name="pause", help="Pauses the currently playing song.\nUsage: !pause")
    async def pause(self, ctx):
        """
        Function to pause the currently playing music.
        """

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("⏸️ Paused the song.")
            logger.info("pause: Paused the song.")
        else:
            await ctx.send("❌ The bot is not playing anything at the moment.")
            logger.warning("pause: Attempted to pause when the bot is not playing.")

    @commands.command(name="stop", help="Stops the currently playing song.\nUsage: !stop")
    async def stop(self, ctx):
        """
        Function to stop playing the music.
        """

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            self.manually_stopped = True
            voice_client.stop()
            await ctx.send("⏹️ Stopped the song.")
            logger.info("stop: Stopped the song.")
        else:
            await ctx.send("❌ The bot is not playing anything at the moment.")
            logger.warning("stop: Attempted to stop when the bot is not playing.")

    @commands.command(name="skip", aliases=["next", "next_song"], help="To play the next song in the queue.\nUsage: !skip")
    async def next_song(self, ctx):
        """
        Function to play the next song in the queue.
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        next_song = self.songs_queue.next_song()
        if isinstance(next_song, int):
            await ctx.send("❌ Unable to retrieve the next song.")
            logger.error(f"next_song: Received error code {next_song}.")
            return

        await self.play_song(next_song, ctx)
        logger.info("next_song: Skipped to the next song.")

    @commands.command(name="prev", aliases=["prev_song"], help="To play the previous song in the queue.\nUsage: !prev")
    async def prev(self, ctx):
        """
        Function to play the previous song in the queue.
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        prev_song = self.songs_queue.prev_song()
        if isinstance(prev_song, int):
            await ctx.send("❌ Unable to retrieve the previous song.")
            logger.error(f"prev: Received error code {prev_song}.")
            return

        await self.play_song(prev_song, ctx)
        logger.info("prev: Moved to the previous song.")

    @commands.command(name="replay", help="Replays the current song.\nUsage: !replay")
    async def replay(self, ctx):
        """
        Function to replay the current song in the queue.
        """

        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            current_song = self.songs_queue.current_song()
            if isinstance(current_song, int):
                await ctx.send("❌ Unable to retrieve the current song.")
                logger.error(f"replay: Received error code {current_song}.")
                return
            await self.play_song(current_song, ctx)
            await ctx.send("🔄 Replayed the current song.")
            logger.info("replay: Replayed the current song.")
        else:
            await ctx.send("❌ The bot is not playing anything at the moment.")
            logger.warning("replay: Attempted to replay when the bot is not playing.")

    @commands.command(name="volume", help="Adjusts the playback volume.\nUsage: !volume <0-100>")
    async def volume(self, ctx, volume: int):
        """
        Adjusts the playback volume.

        Parameters:
            volume (int): Volume level (0-100).
        """
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client or not voice_client.is_connected():
            await ctx.send("❌ Bot is not connected to a voice channel.")
            logger.warning("volume: Bot is not connected to any voice channel.")
            return

        if not voice_client.is_playing():
            await ctx.send("❌ No audio is playing currently.")
            logger.warning("volume: No audio is playing.")
            return

        if not 0 <= volume <= 100:
            await ctx.send("❌ Please provide a volume between 0 and 100.")
            logger.warning(f"volume: Invalid volume level {volume}.")
            return

        # Access the PCMVolumeTransformer
        if isinstance(voice_client.source, PCMVolumeTransformer):
            voice_client.source.volume = volume / 100.0
            await ctx.send(f"🔊 Volume set to {volume}%")
            logger.info(f"volume: Volume set to {volume}%.")
        else:
            await ctx.send("❌ Unable to adjust volume.")
            logger.error("volume: Current audio source is not a PCMVolumeTransformer.")

async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Songs(bot))
