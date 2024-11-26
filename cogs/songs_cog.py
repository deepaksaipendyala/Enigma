# cogs/songs_cog.py
"""
This file contains all bot commands related to songs, such as !poll for generating recommendations,
!next_song for playing the next song, and so on.
"""

import asyncio
import discord
import random
import shlex
from discord.ext import commands
from cogs.helpers.get_all import *
from cogs.helpers.utils import (
    searchSong,
    fetch_spotify_metadata,
    random_n
)
from cogs.helpers.songs_queue import Songs_Queue
import yt_dlp as youtube_dl
import logging
from typing import Tuple, Union
from discord import PCMVolumeTransformer

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

    async def handle_play_next(self, ctx):
        """
        Handles playing the next song in the queue after the current song finishes.
        """
        next_song = self.songs_queue.next_song()
        if isinstance(next_song, int):
            await ctx.send("❌ No more songs in the queue.")
            logger.info("handle_play_next: No more songs in the queue.")
            # Optionally, disconnect from the voice channel
            voice_client = ctx.voice_client
            if voice_client:
                await voice_client.disconnect()
                logger.info("handle_play_next: Disconnected from voice channel due to empty queue.")
            return

        await self.play_song(ctx, next_song)
        logger.info(f"handle_play_next: Playing next song '{next_song[0]}' by '{next_song[1]}'.")

    async def play_song(self, song_tuple: Union[tuple, int], ctx):
        """
        Helper function for playing a song in the voice channel.

        Parameters:
            song_tuple (tuple or int): The song to play as (song_name, artist, source, url) or an error code.
            ctx (commands.Context): The context from Discord.
        """

        logger.debug(f"play_song: Received song_tuple: {song_tuple}, type: {type(song_tuple)}")

        # Handle error codes
        if isinstance(song_tuple, int):
            await ctx.send("❌ Unable to retrieve the next song.")
            logger.error(f"play_song: Received error code {song_tuple}.")
            return

        # Validate song_tuple structure
        if not isinstance(song_tuple, tuple) or len(song_tuple) != 4:
            await ctx.send("❌ Invalid song format.")
            logger.error("play_song: Invalid song format received.")
            return

        logger.info(f"Tuple after play_song access '{song_tuple}'.")
        song_name, artist, source, url = song_tuple
        logger.debug(f"play_song: Preparing to play '{song_name}' by '{artist}'.")

        # Determine the song URL based on the source
        if source.lower() == "url":
            song_url = url if url else song_name  # Use 'url' if available, else 'song_name'
        else:
            song_url = searchSong(song_name, artist)  # Ensure this returns a valid YouTube URL

        if not song_url:
            await ctx.send(f"❌ Unable to find a YouTube link for **{song_name}** by *{artist}*.")
            logger.warning(f"play_song: No YouTube URL found for '{song_name}' by '{artist}'.")
            return

        # If source is not 'url', extract the direct audio stream using youtube_dl
        if source.lower() != "url":
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'source_address': '0.0.0.0'  # Bind to IPv4 to prevent IPv6 issues
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    logger.debug(f"play_song: Extracting audio URL for '{song_url}' using youtube_dl.")
                    info = ydl.extract_info(song_url, download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    song_url = info.get('url')
                    if not song_url:
                        raise Exception("youtube_dl did not return a valid audio URL.")
            except Exception as e:
                await ctx.send("❌ Could not extract audio URL from the song.")
                logger.error(f"play_song: Error extracting audio URL from '{song_url}' - {e}")
                return

        # Get or connect to the voice client
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            try:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
                logger.info(f"play_song: Connected to voice channel '{channel.name}'.")
            except AttributeError:
                await ctx.send("❌ You are not connected to a voice channel.")
                logger.warning("play_song: User is not in a voice channel.")
                return
            except Exception as e:
                await ctx.send(f"❌ Error connecting to voice channel: {e}")
                logger.error(f"play_song: Error connecting to voice channel - {e}")
                return

        # Stop current playback if any
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
            logger.info("play_song: Stopped current playback.")
            await asyncio.sleep(0.5)  # Small delay to ensure playback has stopped
            if voice_client.is_playing():
                await ctx.send("❌ Unable to stop the current song.")
                logger.error("play_song: Unable to stop the current song.")
                return

        # Define FFmpeg options to prevent multiple -ac and -ar warnings
        ffmpeg_options = {
            'options': '-vn',  # No video
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

        # Create FFmpegPCMAudio source and wrap with PCMVolumeTransformer
        try:
            source = discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
            player = PCMVolumeTransformer(source, volume=1.0)  # Default volume at 100%
            logger.debug(f"play_song: Created PCMVolumeTransformer for '{song_url}'.")
        except Exception as e:
            await ctx.send("❌ An error occurred while processing the audio.")
            logger.error(f"play_song: Error creating PCMVolumeTransformer - {e}")
            return

        # Define the after callback function
        def after_playback(error):
            if error:
                logger.error(f"Playback error: {error}")
                # Schedule the coroutine to send a message about the error
                asyncio.run_coroutine_threadsafe(
                    ctx.send(f"❌ An error occurred during playback: {error}"),
                    self.bot.loop
                )
            else:
                # Schedule the coroutine to handle the next song
                asyncio.run_coroutine_threadsafe(
                    self.handle_play_next(ctx),
                    self.bot.loop
                )

        # Play the audio with the after callback
        try:
            voice_client.play(player, after=after_playback)
            await ctx.send(f"🎶 Now playing: **{song_name}** by *{artist}*")
            logger.info(f"play_song: Playing '{song_name}' by '{artist}'.")
        except Exception as e:
            await ctx.send("❌ An error occurred while trying to play the song.")
            logger.error(f"play_song: Exception occurred - {e}")
            return

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
                try:
                    await voice_client.move_to(channel)
                    await ctx.send(f"✅ Moved to voice channel: '{channel.name}'.")
                    logger.info(f"join: Moved to voice channel '{channel.name}'.")
                except Exception as e:
                    await ctx.send(f"❌ Error moving to voice channel: {e}")
                    logger.error(f"join: Error moving to voice channel '{channel.name}': {e}")
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

    @commands.command(name="add", help="Add a song to the queue from YouTube, SoundCloud, or a URL.\nUsage: !add <source> <song_name/URL>")
    async def add(self, ctx, source: str, *, query: str):
        """
        Add a song to the queue from a specified source (YouTube, SoundCloud, or URL).

        Parameters:
            source (str): Source ('yt', 'sc', or 'url').
            query (str): Song name or URL.
        """
        source = source.lower()
        if source not in ["yt", "sc", "url"]:
            await ctx.send("❌ Invalid source. Use 'yt', 'sc', or 'url'.")
            logger.warning(f"add: Invalid source '{source}' provided.")
            return

        if source == "url":
            song_tuple = (query, "Unknown", "url", query)
            self.songs_queue.add_to_queue([song_tuple])
            logger.info(f"add: Added URL '{query}' to the queue.")
        else:
            metadata = fetch_spotify_metadata(query)
            if not metadata:
                await ctx.send(f"❌ Could not find the song **{query}**.")
                logger.warning(f"add: Song '{query}' not found in Spotify metadata.")
                return
            song_tuple = (metadata['track_name'], metadata['artist'], source, None)
            self.songs_queue.add_to_queue([song_tuple])
            logger.info(f"add: Added '{metadata['track_name']}' by '{metadata['artist']}' from source '{source}' to the queue.")

        await ctx.send(f"✅ Added **{query}** to the queue.")

    @commands.command(name="play", aliases=["play_song"], help="To play a song.\nUsage: !play <song_name>")
    async def play(self, ctx, source: str, *, query: str):
        """
        Plays the specified song or the current song in the queue.

        Parameters:
            ctx (commands.Context): The context of the command.
            song_tuple (tuple, optional): The song to play as (song_name, artist, source, url).
                                        If None, fetches the current song from the queue.
        """

        # Fetch the current song from the queue if not explicitly provided
        if source is None and query is None:
            song_tuple = self.songs_queue.current_song()

        source = source.lower()
        if source not in ["yt", "sc", "url"]:
            await ctx.send("❌ Invalid source. Use 'yt', 'sc', or 'url'.")
            logger.warning(f"play: Invalid source '{source}' provided.")
            return

        if source == "url":
            song_tuple = (query, "Unknown", "url", query)
            logger.info(f"Found Song: Playing URL '{query}' Now.")
        else:
            metadata = fetch_spotify_metadata(query)
            if not metadata:
                await ctx.send(f"❌ Could not find the song **{query}**.")
                logger.warning(f"play: Song '{query}' not found in Spotify metadata.")
                return
            song_tuple = (metadata['track_name'], metadata['artist'], source, None)

        # Validate the song tuple
        if not isinstance(song_tuple, (tuple, list)) or len(song_tuple) < 4:
            await ctx.send("❌ No valid song found in the queue.")
            logger.warning(f"play_song: Invalid song data: {song_tuple}")
            return
        song_name, artist, source, url = song_tuple
        logger.debug(f"play_song: Attempting to play '{song_name}' by '{artist}' from source '{source}'.")

        # Determine the URL based on the source
        if source == "url":
            song_url = url
        else:
            song_url = searchSong(song_name, artist)

        if not song_url:
            await ctx.send(f"❌ Could not find the song **{song_name}**.")
            logger.warning(f"play_song: Song URL not found for '{song_name}' by '{artist}'.")
            return

        # Get or connect to the voice client
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            try:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
                logger.info(f"play_song: Connected to voice channel '{channel.name}'.")
            except AttributeError:
                await ctx.send("❌ You are not connected to a voice channel.")
                logger.warning("play_song: User is not in a voice channel.")
                return

        if voice_client.is_playing():
            voice_client.stop()

        # Fetch and play the audio source
        try:
            async with ctx.typing():
                audio_data = await get_audio_source(song_url, song_name, artist, loop=self.bot.loop, stream=True)
                if audio_data is None:
                    await ctx.send("❌ Could not retrieve the audio source.")
                    logger.error(f"play_song: Failed to retrieve audio for '{song_name}'.")
                    return
                player, data = audio_data
                voice_client.play(player, after=lambda _: asyncio.run_coroutine_threadsafe(self.next_song(ctx), self.bot.loop))
                await ctx.send(f"🎶 Now playing: **{song_name}** by *{artist}* ({source}).")
                logger.info(f"play_song: Playing '{song_name}' by '{artist}' ({source}).")
        except Exception as e:
            await ctx.send("❌ An error occurred while trying to play the song.")
            logger.error(f"play_song: Exception occurred - {e}")


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
        metadata = await loop.run_in_executor(None, fetch_spotify_metadata, song_name)
        logger.info(f"metadata:'{metadata}'.")
        if metadata:
            song_tuple = (metadata['track_name'], metadata['artist'], 'spotify', None)
            self.songs_queue.add_to_queue([song_tuple])
            logger.info(f"fetch_and_add_song: Added '{song_tuple[0]}' by '{song_tuple[1]}' to the queue.")
            return song_tuple
        else:
            logger.warning(f"fetch_and_add_song: Song '{song_name}' not found on Spotify.")
            return None

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
    async def next_song_command(self, ctx):
        """
        Function to play the next song in the queue.
        """

        # Handle empty queue
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        # Get the voice client
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("❌ I'm not connected to a voice channel.")
            logger.warning("next_song_command: Bot is not connected to any voice channel.")
            return

        if voice_client.is_playing():
            voice_client.stop()  # Stop the currently playing song
            logger.info("next_song_command: Stopped the current song.")

        # Retrieve the next song from the queue
        next_song = self.songs_queue.next_song()
        if isinstance(next_song, int):
            await ctx.send("❌ Unable to retrieve the next song.")
            logger.error(f"next_song_command: Received error code {next_song}.")
            return

        # Play the next song
        await self.play_song(next_song, ctx)
        logger.info(f"next_song_command: Skipped to the next song '{next_song[0]}' by '{next_song[1]}'.")
        await ctx.send(f"✅ Skipped to **{next_song[0]}** by *{next_song[1]}*.")

    @commands.command(name="prev", aliases=["prev_song"], help="To play the previous song in the queue.\nUsage: !prev")
    async def prev_song_command(self, ctx):
        """
        Function to play the previous song in the queue.
        """

        # Handle empty queue
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        # Get the voice client
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("❌ I'm not connected to a voice channel.")
            logger.warning("prev_song_command: Bot is not connected to any voice channel.")
            return

        if voice_client.is_playing():
            voice_client.stop()  # Stop the currently playing song
            logger.info("prev_song_command: Stopped the current song.")

        # Retrieve the previous song from the queue
        prev_song = self.songs_queue.prev_song()
        if isinstance(prev_song, int):
            await ctx.send("❌ Unable to retrieve the previous song.")
            logger.error(f"prev_song_command: Received error code {prev_song}.")
            return

        # Play the previous song
        await self.play_song(prev_song, ctx)
        logger.info(f"prev_song_command: Moved to the previous song '{prev_song[0]}' by '{prev_song[1]}'.")
        await ctx.send(f"✅ Moved to previous song: **{prev_song[0]}** by *{prev_song[1]}*.")

    @commands.command(name="replay", help="Replays the current song.\nUsage: !replay")
    async def replay_song(self, ctx):
        """
        Function to replay the current song in the queue.
        """

        # Handle empty queue
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if empty_queue:
            return

        # Get the voice client
        voice_client = ctx.voice_client

        if not voice_client or not voice_client.is_connected():
            await ctx.send("❌ I'm not connected to a voice channel.")
            logger.warning("replay_song: Bot is not connected to any voice channel.")
            return

        if voice_client.is_playing():
            voice_client.stop()  # Stop the currently playing song
            logger.info("replay_song: Stopped the current song for replay.")

        # Retrieve the current song from the queue
        current_song = self.songs_queue.current_song()
        if isinstance(current_song, int):
            await ctx.send("❌ Unable to retrieve the current song.")
            logger.error(f"replay_song: Received error code {current_song}.")
            return

        # Play the current song again
        await self.play_song(current_song, ctx)
        logger.info(f"replay_song: Replayed the current song '{current_song[0]}' by '{current_song[1]}'.")
        await ctx.send("🔄 Replayed the current song.")


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

    @commands.command(name='mood', help='Recommend songs based on your mood or activity.\nUsage: !mood')
    async def mood_recommend(self, ctx):
        """
        Recommends songs based on the user's mood or activity.
        """
        # Send an embed message with mood options.
        mood_options = {
            '😊': 'happy',
            '😢': 'sad',
            '🎉': 'party',
            '😌': 'chill',
            '❤️': 'romantic',
        }

        # Create an embed message with the options.
        mood_embed = discord.Embed(
            title="Choose Your Mood",
            description="React with the corresponding emoji to select your mood:\n\n"
                        "😊 - Happy\n"
                        "😢 - Sad\n"
                        "🎉 - Party\n"
                        "😌 - Chill\n"
                        "❤️ - Romantic",
            color=discord.Color.blue()
        )

        # Send the embed message and add reaction options.
        message = await ctx.send(embed=mood_embed)
        for emoji in mood_options:
            await message.add_reaction(emoji)

        # Function to check if the reaction is one of the valid ones.
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in mood_options and reaction.message.id == message.id

        try:
            # Wait for a single reaction from the user.
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            selected_mood = mood_options[str(reaction.emoji)]

            # Confirm the selected mood to the user.
            await ctx.send(f"You selected: {selected_mood.capitalize()}")

            # # Remove all reactions to prevent further selections.
            # await message.clear_reactions()
        except asyncio.TimeoutError:
            await ctx.send("⏰ You took too long to respond! Please try again.")
            logger.warning("mood_recommend: User did not respond in time.")
            return

        # Define mood filters based on EDA analysis.
        mood_map = {
            'happy': {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)},
            'sad': {'sadness': (0.5, 1), 'valence': (0.0, 0.3), 'energy': (0.2, 0.5)},
            'party': {'danceability': (0.7, 1.0), 'valence': (0.6, 1.0), 'energy': (0.6, 1.0)},
            'chill': {'acousticness': (0.6, 1.0), 'energy': (0.1, 0.5)},
            'romantic': {'romantic': (0.5, 1.0), 'valence': (0.2, 0.5)},
        }

        filters = mood_map[selected_mood]
        recommended_songs = get_recommended_songs_based_on_mood(filters)
        logger.info(f"recommended_songs: {recommended_songs}")

        if not recommended_songs:
            await ctx.send("❌ No songs found for the selected mood.")
            logger.warning(f"mood_recommend: No songs found for mood '{selected_mood}'.")
            return

        # Debugging: Log the structure of recommended_songs
        for idx, song in enumerate(recommended_songs, 1):
            logger.debug(f"Recommended Song {idx}: {song}, Type: {type(song)}")

        # Adjust the list comprehension based on the structure of recommended_songs
        try:
            if all(isinstance(song, dict) for song in recommended_songs):
                # If recommended_songs is a list of dictionaries
                song_tuples = [
                    (song['track_name'], song['artist'], 'Dataset', None)
                    for song in recommended_songs
                ]
            elif all(isinstance(song, tuple) for song in recommended_songs):
                # If recommended_songs is a list of tuples
                song_tuples = [
                    (song[0], song[1], 'Dataset', None)
                    for song in recommended_songs
                ]
            elif all(isinstance(song, str) for song in recommended_songs):
                # If recommended_songs is a list of strings
                song_tuples = [
                    (song, 'Unknown', 'Dataset', None)
                    for song in recommended_songs
                ]
            else:
                await ctx.send("❌ Unexpected song data format.")
                logger.error("mood_recommend: Unexpected song data format in recommended_songs.")
                return
        except Exception as e:
            await ctx.send("❌ Error processing recommended songs.")
            logger.error(f"mood_recommend: Error processing recommended songs - {e}")
            return

        if not song_tuples:
            logger.info(f"Song Tuples: {song_tuples}")
            await ctx.send("❌ No valid songs found for the selected mood.")
            logger.warning(f"mood_recommend: No valid songs found after processing.")
            return

        # Add recommendations to queue and play.
        self.songs_queue.clear()
        self.songs_queue.add_to_queue(song_tuples)
        current_song = self.songs_queue.current_song()
        await self.play_song(current_song, ctx)
        logger.info(f"mood_recommend: Added and playing recommended songs for mood '{selected_mood}'.")



async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Songs(bot))
