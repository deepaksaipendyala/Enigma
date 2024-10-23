"""
This file is responsible for all bot commands regarding songs such /poll for generating recommendations,
/next_song for playing next song and so on
"""
import asyncio
import discord
from src.get_all import *
from dotenv import load_dotenv
from discord.ext import commands
from src.utils import searchSong, random_25
from src.songs_queue import Songs_Queue
import yt_dlp as youtube_dl


FFMPEG_OPTIONS = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': [
        'ffmpeg', '-i', './assets/sample.mp4', '-vn', '-f', 'mp3',
        './assets/sample.mp3'
    ]
}
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}

def get_audio_sorce(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': 'in_playlist',
        'noplaylist': True,
        'no_warnings': True,
        'cookies': '../cookies.txt',
        'outtmpl': 'downloaded_music/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        return discord.FFmpegOpusAudio(audio_url, **FFMPEG_OPTIONS)

class Songs(commands.Cog):
    """
    Cog for bot that handles all commands related to songs
    """

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='join', help='To join the voice channel')
    async def join(self, ctx, channel: discord.VoiceChannel = None):
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


    """
    Function for handling resume capability
    """

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play command"
            )

    """
    Function for playing a custom song
    """

    @commands.command(name='play_custom', help='To play custom song')
    async def play_custom(self, ctx):
        user_message = str(ctx.message.content)
        song_name = user_message.split(' ', 1)[1]
        await self.play_song(song_name, ctx)

    """
    Function to stop playing the music
    """

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    """
    Helper function for playing song on the voice channel
    """

    async def play_song(self, song_name, ctx):
        
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

    """
    Helper function to handle empty song queue
    """

    async def handle_empty_queue(self, ctx):
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

    """
    Function to play the next song in the queue
    """

    @commands.command(name='next_song', help='To play next song in queue')
    async def next_song(self, ctx):
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.next_song(), ctx)

    """
    Function to play the previous song in the queue
    """

    @commands.command(name='prev_song', help='To play prev song in queue')
    async def play(self, ctx):
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            await self.play_song(songs_queue.prev_song(), ctx)

    """
    Function to pause the music that is playing
    """

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    """
    Function to generate poll for playing the recommendations
    """

    @commands.command(name='poll', help='Poll for recommendation')
    async def poll(self, ctx):
        reactions = ['👍', '👎']
        selected_songs = []
        count = 0
        bot_message = "Select song preferences by reaction '👍' or '👎' to the choices. \nSelect 3 songs"
        await ctx.send(bot_message)
        ten_random_songs = random_25()
        for ele in zip(ten_random_songs["track_name"],
                       ten_random_songs["artist"]):
            bot_message = str(ele[0]) + " By " + str(ele[1])
            description = []
            poll_embed = discord.Embed(title=bot_message,
                                       color=0x31FF00,
                                       description=''.join(description))
            react_message = await ctx.send(embed=poll_embed)
            for reaction in reactions[:len(reactions)]:
                await react_message.add_reaction(reaction)
            res, user = await self.bot.wait_for('reaction_add')
            if (res.emoji == u'👍'):
                selected_songs.append(str(ele[0]))
                count += 1
            if (count == 3):
                bot_message = "Selected songs are : " + \
                    ' , '.join(selected_songs)
                await ctx.send(bot_message)
                break
        global songs_queue
        recommended_songs = recommend(selected_songs)
        songs_queue = Songs_Queue(recommended_songs)
        await self.play_song(songs_queue.next_song(), ctx)

    """
    Function to display all the songs in the queue
    """

    @commands.command(name='queue', help='Show active queue of recommendations')
    async def queue(self, ctx):
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            queue, index = songs_queue.return_queue()
            await ctx.send("Queue of recommendations: ")
            for i in range(len(queue)):
                if i == index:
                    await ctx.send("Currently Playing: " + queue[i])
                else:
                    await ctx.send(queue[i])

    """
    Function to shuffle songs in the queue
    """

    @commands.command(name='shuffle', help='To shuffle songs in queue')
    async def shuffle(self, ctx):
        empty_queue = await self.handle_empty_queue(ctx)
        if not empty_queue:
            songs_queue.shuffle_queue()
            await ctx.send("Playlist shuffled")

    """
    Function to add custom song to the queue
    """

    @commands.command(name='add_song', help='To add custom song to the queue')
    async def add_song(self, ctx):
        user_message = str(ctx.message.content)
        song_name = user_message.split(' ', 1)[1]
        songs_queue.add_to_queue(song_name)
        await ctx.send("Song added to queue")

    @commands.command(name='mood_recommend', help='Songs based on your mood or activity')
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
        global songs_queue
        songs_queue = Songs_Queue(recommended_songs)
        await self.play_song(songs_queue.next_song(), ctx)


"""
    Function to add the cog to the bot
"""
async def setup(client):
    await client.add_cog(Songs(client))
