import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext.commands import Bot, Context
from discord import Intents


# Patch Spotify before importing the Songs cog
with patch("spotipy.oauth2.SpotifyClientCredentials", MagicMock()), \
     patch("cogs.helpers.utils.spotify", MagicMock()):
    from cogs.songs_cog import Songs  # Import your cog




@pytest.mark.asyncio
async def test_volume_command_bot_not_in_voice_channel():
    # Mock the bot with required intents
    intents = Intents.default()
    bot = Bot(command_prefix="!", intents=intents)
    
    # Add the Songs cog
    cog = Songs(bot)
    await bot.add_cog(cog)
    
    # Mock the Discord context
    ctx = MagicMock(spec=Context)
    ctx.guild = MagicMock()
    ctx.send = AsyncMock()
    
    # Case: No voice client (bot not in a voice channel)
    ctx.voice_client = None
    volume = 50  # Attempt to set volume to 50%
    await cog.volume(ctx, volume)
    ctx.send.assert_called_once_with("❌ Bot is not connected to a voice channel.")
