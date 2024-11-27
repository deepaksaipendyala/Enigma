import pytest
from unittest.mock import AsyncMock, MagicMock
from discord.ext.commands import Bot, Context
from cogs.songs_cog import Songs  # Import the cog containing the !volume command

@pytest.mark.asyncio


async def test_volume_command1():
    # Mock the bot
    bot = Bot(command_prefix="!")
    
    # Add the Songs cog
    cog = Songs(bot)
    await bot.add_cog(cog)
    
    # Mock the Discord context and voice client
    ctx = MagicMock(spec=Context)
    ctx.guild = MagicMock()
    ctx.send = AsyncMock()
    ctx.voice_client = MagicMock()
    
    # Set up the mocked voice client
    ctx.voice_client.is_connected.return_value = True
    ctx.voice_client.is_playing.return_value = True
    ctx.voice_client.source = MagicMock()
    ctx.voice_client.source.volume = 1.0  # Initial volume

    # Case 1: Valid volume
    volume = 50  # Set volume to 50%
    await cog.volume(ctx, volume)
    ctx.voice_client.source.volume = volume / 100.0  # Volume should be updated
    ctx.send.assert_called_once_with("🔊 Volume set to 50%")

    # Reset mocks for the next case
    ctx.send.reset_mock()

async def test_volume_command2():
    # Mock the bot
    bot = Bot(command_prefix="!")
    
    # Add the Songs cog
    cog = Songs(bot)
    await bot.add_cog(cog)
    
    # Mock the Discord context and voice client
    ctx = MagicMock(spec=Context)
    ctx.guild = MagicMock()
    ctx.send = AsyncMock()
    ctx.voice_client = MagicMock()
    
    # Set up the mocked voice client
    ctx.voice_client.is_connected.return_value = True
    ctx.voice_client.is_playing.return_value = True
    ctx.voice_client.source = MagicMock()
    ctx.voice_client.source.volume = 1.0  # Initial volume

    # Case 1: Valid volume
    volume = 50  # Set volume to 50%
    await cog.volume(ctx, volume)
    ctx.voice_client.source.volume = volume / 100.0  # Volume should be updated
    ctx.send.assert_called_once_with("🔊 Volume set to 50%")

    # Reset mocks for the next case
    ctx.send.reset_mock()
    
    # Case 2: Invalid volume (out of range)
    invalid_volume = 150
    await cog.volume(ctx, invalid_volume)
    ctx.send.assert_called_once_with("❌ Please provide a volume between 0 and 100.")