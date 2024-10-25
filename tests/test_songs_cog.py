import pytest
import unittest
from cogs.songs_cog import *
import warnings
import sys

sys.path.append("../")

warnings.filterwarnings("ignore")


@pytest.mark.asyncio
class Test_Songs_Cog(unittest.TestCase):

    async def test_resume(self):
        result = await Songs.resume()
        assert (
            result == "The bot was not playing anything before this. Use play command"
        )

    async def test_stop(self):
        result = await Songs.stop()
        assert result == "The bot is not playing anything at the moment."

    async def test_play_song(self):
        result = await Songs.play_song()
        assert result == "The bot is not connected to a voice channel."

    async def test_handle_empty_queue(self):
        result = await Songs.handle_empty_queue()
        assert (
            result
            == "No recommendations present. First generate recommendations using /poll"
        )

    async def test_pause(self):
        result = await Songs.pause()
        assert result == "The bot is not playing anything at the moment."

    async def test_shuffle(self):
        result = await Songs.shuffle()
        assert result == "Playlist shuffled"

    async def test_add_song(self):
        result = await Songs.add_song()
        assert result == "Song added to queue"