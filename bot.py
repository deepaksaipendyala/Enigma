# bot.py
"""
This file is the main entry point of the bot.
"""

import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import http.server
import socketserver
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Health Check Server Setup
Handler = http.server.SimpleHTTPRequestHandler

def start_health_check_server():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logger.info(f"Health check server running on port {PORT}")
        httpd.serve_forever()

# Start the health check server in a separate thread
thread = threading.Thread(target=start_health_check_server)
thread.daemon = True
thread.start()

# Load environment variables
load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Bot with necessary intents and disable default help command
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

"""
Function that gets executed once the bot is initialized.
"""
@bot.event
async def on_ready():
    logger.info(f"Bot is ready as {bot.user}")

    logger.info("Loading all cogs")
    # Get all the files that end with _cog.py in the ./cogs directory
    for filename in os.listdir("./cogs"):
        if filename.endswith("_cog.py"):
            cog_name = filename[:-3]
            cog_path = f"cogs.{cog_name}"
            try:
                await bot.load_extension(cog_path)
                logger.info(f"{cog_name} loaded successfully")
            except Exception as e:
                logger.error(f"Error loading cog {cog_path}: {e}")

    # Connect to the "Lounge" voice channel if not already connected
    channel = discord.utils.get(bot.get_all_channels(), name="Lounge")
    if channel:
        existing_voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if existing_voice_client and existing_voice_client.channel == channel:
            logger.info(f"Bot already connected to voice channel: {channel.name}")
        else:
            try:
                await channel.connect()
                logger.info(f"Bot connected to voice channel: {channel.name}")
            except Exception as e:
                logger.error(f"Error connecting to voice channel: {e}")
    else:
        logger.error("Voice channel 'Lounge' not found. Use the 'join' command to connect.")

"""
Function that is executed once any message is received by the bot.
"""
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Process commands regardless of channel unless specified
    await bot.process_commands(message)

"""
Start the bot.
"""
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run the bot: {e}")
