"""
dThis file is the main entry point of the bot
"""

from multiprocessing.util import debug
import discord
import os
from cogs.helpers.get_all import *
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
client = commands.Bot(command_prefix="!", intents=intents)
"""
Function that gets executed once the bot is initialized
"""


@client.event
async def on_ready():
    print(f"Bot is ready as {client.user}")

    try:
        print("Loading all cogs")
        # Get all the files that end in _cog.py
        for filename in os.listdir("./cogs"):
            if filename.endswith("_cog.py"):
                # Load the cog
                cog_name = filename[:-3]
                cog_path = f"cogs.{cog_name}"

                await client.load_extension(cog_path)
        print("Cogs loaded successfully")
    except Exception as e:
        print(f"Error loading cog {cog_path}: {e}")

    # By defaul, try to join a voice channel named "General"

    # voice_channel = client.get_channel(VOICE_CHANNEL_ID)

    channel = discord.utils.get(client.get_all_channels(), name="General")

    if channel is not None:
        channel = channel.id
        voice_channel = client.get_channel(channel)

    if (channel is not None) and (client.user not in voice_channel.members):
        await voice_channel.connect()
        print("Bot connected to voice channel")
    else:
        print("Error connecting to General. See the 'join' command for help.")


"""
Function that is executed once any message is received by the bot
"""


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "general":
        await client.process_commands(message)


"""
Start the bot
"""
client.run(TOKEN)
