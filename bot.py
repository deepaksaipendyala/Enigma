"""
dThis file is the main entry point of the bot
"""

from multiprocessing.util import debug
import discord
import os
from src.get_all import *
import re
from dotenv import load_dotenv
from discord.ext import commands
from src.utils import searchSong
from src.songs_queue import Songs_Queue
from src.songs_cog import Songs

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

    



"""
Function that is executed once any message is received by the bot
"""


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # options = set()

    # if message.channel.name == 'general':
    #     user_message = str(message.content)
    await client.process_commands(message)


"""
Start the bot
"""
client.run(TOKEN)
