"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""

import asyncio
import discord
from helpers.get_all import *
from discord.ext import commands
from helpers.utils import searchSong, random_25
from helpers.songs_queue import Songs_Queue
import yt_dlp as youtube_dl


FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

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
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(YDL_OPTIONS)


async def get_audio_sorce(url: str, *, loop=None, stream=False):

    loop = loop or asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

    if "entries" in data:
        data = data["entries"][0]

    filename = data["url"] if stream else youtube_dl.prepare_filename(data)
    print(f"filename: {filename}")
    return (discord.FFmpegOpusAudio(filename, **FFMPEG_OPTIONS), data)


class Songs(commands.Cog):
    """
    Cog for bot that handles all commands related to songs
    """

    

    def __init__(self, bot):
        self.bot = bot
        self.manually_stopped = False
        # Initialize the songs queue
        self.songs_queue = Songs_Queue()


    #-----------Helper Functions-----------#

    def handle_play_next(self, ctx):
        if not self.manually_stopped and not ctx.voice_client.is_playing():
            asyncio.run_coroutine_threadsafe(self.play_song(self.songs_queue.next_song(), ctx), self.bot.loop)

    async def play_song(self, song_name, ctx):
        """
        Helper function for playing song on the voice channel

        Parameters:
            song_name (str): The name of the song to play
        """

        # Get the song URL
        url = searchSong(song_name)
        print(url)

        bot_client = None

        # Get the voice client for the guild
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        
        if not voice_client:
            await ctx.send("Bot is not connected to a voice channel")
            return

        # Check if the bot is already playing a song, and stop it if it is
        if voice_client.is_playing():
            self.manually_stopped = True
            voice_client.stop()

        # Get and play the audio source
        # audio_source = get_audio_sorce(url)
        # ctx.voice_client.play(audio_source, after=lambda e: self.handle_play_next(ctx), )

        async with ctx.typing():
            print("Getting audio source")
            player, data = await get_audio_sorce(url, loop=self.bot.loop, stream=True)
            print(f"Starting playback of {data['title']}")
            voice_client.play(player, after=lambda e: print(f"player error {e}") if e else self.handle_play_next(ctx)) #
            
            if not ctx.voice_client.is_playing():
                print ("Playback error")
            else:
                print("Playing")

        await ctx.send(f"Now playing: {url}")
        self.manually_stopped = False


    #-----------Commands-----------#


    @commands.command(name="join", help="To join the voice channel")
    async def join(self, ctx, channel_name: str = commands.parameter(description="The voice channel to join (optional)", default=None)):
        """
        Function for joining the voice channel

        Parameters:
            channel (discord.VoiceChannel): The voice channel to join
        """

        if not channel_name:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("No channel to join. Please specify a channel")
                return    

        # Get the voice channel object
        channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        # Check if the bot is already connected to that channel
        if channel: 
            # get the current voice client for the bot in the guild
            bot_channel = discord.utils.get(ctx.bot.voice_clients, guild=channel.guild)
            if bot_channel and bot_channel.channel.name == channel.name:
                await ctx.send(f"Already connected to {channel_name}")
                return
            elif bot_channel:
                try:
                    await bot_channel.move_to(channel)
                    await ctx.send(f"Connected to {channel_name}")
                except Exception as e:
                    await ctx.send(f"Error connecting to {channel_name}: {e}")
            else:
                try:
                    await channel.connect()
                    await ctx.send(f"Connected to {channel_name}")
                except Exception as e:
                    await ctx.send(f"Error connecting to {channel_name}: {e}")
        else:
            await ctx.send(f"Channel {channel_name} not found")
            return


    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx):
        """
        Function for handling resume capability
        """

        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play command"
            )


    @commands.command(name="start", help="Starts playing the current song in the queue")
    async def start(self, ctx):
        """
        Function for starting the song
        """

        if self.songs_queue.get_len() == 0:
            await ctx.send("No songs in the queue. Please add songs to the queue")
            return

        await self.play_song(self.songs_queue.current_song(), ctx)

    @commands.command(
        name="play",
        aliases=["play_song"],
        help="To play user defined song, does not need to be in the database.",
    )
    async def play_custom(self, ctx, song_name: str = commands.parameter(description="The name of the song to play"), artist_name: str = commands.parameter(description="The name of the artist of the song")):
        """
        Function for playing a custom song. PLaying a custom song will clear the queue and begin playing the custom song
        """

        # Check that a song was provided
        if not song_name:
            await ctx.send("Please provide a song to play")
            return
        
        if not artist_name:
            await ctx.send("Please provide an artist name")
            return
        
        song = (song_name, artist_name)

        self.songs_queue.clear()
        self.songs_queue.add_to_queue(song)
        
        current_song = self.songs_queue.current_song()
        print(f"Current song: {current_song}")
        await self.play_song(current_song, ctx)


    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx):
        """
        Function to pause the music that is playing
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await ctx.send("Pausing")
            voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx):
        """
        Function to stop playing the music
        """

        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            self.manually_stopped = True
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


        #TODO: update queue implementation


    @commands.command(name="skip", aliases=["next, next_song"], help="To play next song in queue")
    async def next_song(self, ctx):
        """
        Function to play the next song in the queue
        """
        
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(self.songs_queue.next_song(), ctx)


    @commands.command(name="prev", aliases=["prev_song"], help="To play previous song in queue")
    async def prev(self, ctx):
        """
        Function to play the previous song in the queue
        """
        
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(self.songs_queue.prev_song(), ctx)


    #TODO: update queue implementation
    @commands.command(name="replay", help="This command replays the current song")
    async def replay(self, ctx):
        """
        Function to restart the current song in queue
        """
        
        empty_queue = await self.songs_queue.handle_empty_queue(ctx)
        voice_client = ctx.message.guild.voice_client
        if not empty_queue and voice_client.is_playing():
            voice_client.stop()
        await self.play_song(self.songs_queue.current_song, ctx)


    @commands.command(
        name="poll_old",
        help="Generate a poll to create some recommendations. This is the old version",
    )
    async def poll(self, ctx):
        """
        Function to generate poll for playing the recommendations. Clears the queue and adds the recommendations
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
        
        # Add recommendations to queue and play.
        recommended_songs = recommend(selected_songs)
        self.songs_queue.clear()
        self.songs_queue.add_to_queue(recommended_songs)
        await self.play_song(self.songs_queue.current_song(), ctx)

    
    @commands.command(name='mood', help='Recommend songs based on your mood or activity')
    async def mood_recommend(self, ctx):
        # Send an embed message with mood options.
        mood_options = {
            '😊': 'happy',
            '😢': 'sad',
            '🎉': 'party',
            '😌': 'chill',
            '❤️': 'Romantic',
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
            return user == ctx.message.author and str(reaction.emoji) in mood_options

        try:
            # Wait for a single reaction from the user.
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            selected_mood = mood_options[str(reaction.emoji)]

            # Confirm the selected mood to the user.
            await ctx.send(f"You selected: {selected_mood.capitalize()}")

            # Remove all reactions to prevent further selections.
            await message.clear_reactions()

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond! Please try again.")
            return

        # Define mood filters based on EDA analysis.
        mood_map = {
            'happy': {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)},
            'sad': {'sadness': (0.5, 1), 'valence': (0.0, 0.3), 'energy': (0.2, 0.5)},
            'party': {'danceability': (0.7, 1.0), 'valence': (0.6, 1.0), 'energy': (0.6, 1.0)},
            'chill': {'acousticness': (0.6, 1.0), 'energy': (0.1, 0.5)},
            'Romantic': {'romantic': (0.5, 1.0), 'valence': (0.2, 0.5)},
        }

        filters = mood_map[selected_mood]
        recommended_songs = get_recommended_songs_based_on_mood(filters)

        if not recommended_songs:
            await ctx.send("No songs found for the selected mood.")
            return

        # Add recommendations to queue and play.
        self.songs_queue.clear()
        self.songs_queue.add_to_queue(recommended_songs)
        await self.play_song(self.songs_queue.current_song(), ctx)


async def setup(client: discord.Client):
    """
    Function to add the cog to the bot

    Parameters:
        client (discord.Client): The bot client
    """

    await client.add_cog(Songs(client))
