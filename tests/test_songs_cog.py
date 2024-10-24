import discord
import os
import asyncio
import pytest
import discord.ext.test as dpytest
from discord.ext import commands


@pytest.mark.asyncio
async def test_join(bot):
    guild = dpytest.get_config().guilds[0]
    voice_channel = dpytest.get_config().voice_channels[0]
    await dpytest.message("!join")
    assert dpytest.verify().activity().type(discord.ActivityType.listening)


@pytest.mark.asyncio
async def test_resume(bot):
    # result = await Songs.resume()
    # assert (
    #     result == "The bot was not playing anything before this. Use play command"
    # )

    await dpytest.message("!resume")
    assert (
        dpytest.verify()
        .message()
        .content("The bot is not playing anything at the moment.")
    )


# async def test_stop():
#     result = await Songs.stop()
#     assert result == "The bot is not playing anything at the moment."

# async def test_play_song():
#     result = await Songs.play_song()
#     assert result == "The bot is not connected to a voice channel."

# async def test_handle_empty_queue():
#     result = await Songs.handle_empty_queue()
#     assert (
#         result
#         == "No recommendations present. First generate recommendations using /poll"
#     )

# async def test_pause():
#     result = await Songs.pause()
#     assert result == "The bot is not playing anything at the moment."

# async def test_shuffle():
#     result = await Songs.shuffle()
#     assert result == "Playlist shuffled"

# async def test_add_song():
#     result = await Songs.add_song()
#     assert result == "Song added to queue"
