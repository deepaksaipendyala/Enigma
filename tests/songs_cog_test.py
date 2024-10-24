import discord
import os
import asyncio
import pytest
import discord.ext.test as dpytest
from discord.ext import commands


@pytest.mark.asyncio
class Test_Songs_Cog():
        
    async def test_join(self, bot):
        guild = dpytest.get_config().guilds[0]
        voice_channel = dpytest.get_config().voice_channels[0]
        await dpytest.message("!join")
        assert dpytest.verify().activity().type(discord.ActivityType.listening)

    async def test_resume(self, bot):
        # result = await Songs.resume()
        # assert (
        #     result == "The bot was not playing anything before this. Use play command"
        # )

        await dpytest.message("!resume")
        assert dpytest.verify().message().content("The bot is not playing anything at the moment.")

    # async def test_stop(self):
    #     result = await Songs.stop()
    #     assert result == "The bot is not playing anything at the moment."

    # async def test_play_song(self):
    #     result = await Songs.play_song()
    #     assert result == "The bot is not connected to a voice channel."

    # async def test_handle_empty_queue(self):
    #     result = await Songs.handle_empty_queue()
    #     assert (
    #         result
    #         == "No recommendations present. First generate recommendations using /poll"
    #     )

    # async def test_pause(self):
    #     result = await Songs.pause()
    #     assert result == "The bot is not playing anything at the moment."

    # async def test_shuffle(self):
    #     result = await Songs.shuffle()
    #     assert result == "Playlist shuffled"

    # async def test_add_song(self):
    #     result = await Songs.add_song()
    #     assert result == "Song added to queue"
