"""
dThis file is the main entry point of the bot
"""

from multiprocessing.util import debug
import discord
import os
from src.get_all import *
from dotenv import load_dotenv
from discord.ext import commands
from src.utils import searchSong
from src.songs_queue import Songs_Queue
from src.songs_cog import Songs
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

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')
# This can be obtained using ctx.message.author.voice.channel
VOICE_CHANNEL_ID = 1293317419279843392
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)
"""
Function that gets executed once the bot is initialized
"""


@client.event
async def on_ready():
    print(f'Bot is ready as {client.user}')

    try:
        print("Loading songs cog")
        await client.load_extension("src.songs_cog")
        print("Songs cog loaded successfully")
    except Exception as e:
        print(f"Error loading songs cog: {e}")

    voice_channel = client.get_channel(VOICE_CHANNEL_ID)
    if client.user not in voice_channel.members:
        await voice_channel.connect()
        print("Bot connected to voice channel")

    



"""
Function that is executed once any message is received by the bot
"""


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == 'general':
        await client.process_commands(message)


"""
Start the bot
"""
client.run(TOKEN)
