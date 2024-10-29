"""
This file is the main entry point of the bot
"""

from multiprocessing.util import debug
import discord
import os
from helpers.get_all import *
from dotenv import load_dotenv
from discord.ext import commands

# from cogs.helpers.utils import searchSong
# from cogs.helpers.songs_queue import Songs_Queue
# from cogs.songs_cog import Songs
import http.server
import socketserver
import threading

Handler = http.server.SimpleHTTPRequestHandler


def start_health_check_server():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Health check server running on port {PORT}")
        httpd.serve_forever()


# Start the health check server in a separate thread
thread = threading.Thread(target=start_health_check_server)
thread.daemon = True
thread.start()

load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")
# This can be obtained using ctx.message.author.voice.channel
# VOICE_CHANNEL_ID = 1293317419279843392
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
"""
Function that gets executed once the bot is initialized
"""


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")

    print("Loading all cogs")
    # Get all the files that end in _cog.py
    for filename in os.listdir("./cogs"):
        if filename.endswith("_cog.py"):
            # Load the cog
            cog_name = filename[:-3]
            cog_path = f"cogs.{cog_name}"
            try:
                await bot.load_extension(cog_path)
                print(f"{cog_name} loaded successfully")
            except Exception as e:
                print(f"Error loading cog {cog_path}: {e}")

    # By defaul, try to join a voice channel named "General"

    # voice_channel = client.get_channel(VOICE_CHANNEL_ID)

    channel = discord.utils.get(bot.get_all_channels(), name="General")

    if channel is not None:
        bot_channel = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if bot_channel and bot_channel.name == channel.name:
            print(f"Bot already connected to {bot_channel.name}")
        else:
            try:
                await channel.connect()
                print(f"Bot connected to voice channel: {channel.name}")
            except Exception as e:
                print(f"Error connecting to voice channel: {e}")
    else:
        print("Error connecting to General. See the 'join' command for help.")


"""
Function that is executed once any message is received by the bot
"""


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == "general":
        await bot.process_commands(message)


"""
Start the bot
"""
bot.run(TOKEN)
