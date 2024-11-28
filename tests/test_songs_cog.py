import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from cogs.songs_cog import Songs
from cogs.helpers.songs_queue import Songs_Queue
import discord


@pytest.mark.asyncio
class Test_Songs_Cog(unittest.TestCase):

    def setUp(self):
        # Create a mock bot instance and initialize the Songs cog
        self.bot = MagicMock()
        self.songs_cog = Songs(self.bot)
        self.ctx = MagicMock()  # Mock the context
        self.ctx.author = MagicMock()
        self.ctx.guild = MagicMock()
        self.ctx.voice_client = None

    async def test_resume(self):
        # Test when bot is paused
        self.ctx.voice_client = MagicMock()
        self.ctx.voice_client.is_paused.return_value = True

        with patch.object(self.songs_cog, "bot") as mock_bot:
            result = await self.songs_cog.resume(self.ctx)
            self.ctx.send.assert_called_with("▶️ Resumed the song.")
            self.ctx.voice_client.resume.assert_called_once()

        # Test when bot is not paused
        self.ctx.voice_client.is_paused.return_value = False
        await self.songs_cog.resume(self.ctx)
        self.ctx.send.assert_called_with(
            "❌ The bot is not paused or not playing anything."
        )

    async def test_stop(self):
        # Test when bot is playing
        self.ctx.voice_client = MagicMock()
        self.ctx.voice_client.is_playing.return_value = True

        await self.songs_cog.stop(self.ctx)
        self.ctx.send.assert_called_with("⏹️ Stopped the song.")
        self.ctx.voice_client.stop.assert_called_once()

        # Test when bot is not playing
        self.ctx.voice_client.is_playing.return_value = False
        await self.songs_cog.stop(self.ctx)
        self.ctx.send.assert_called_with(
            "❌ The bot is not playing anything at the moment."
        )

    async def test_play_song(self):
        # Test when no voice channel is connected
        self.ctx.author.voice = None
        await self.songs_cog.play_song(("Test Song", "Test Artist", "yt", None), self.ctx)
        self.ctx.send.assert_called_with("❌ You are not connected to a voice channel.")

    async def test_handle_empty_queue(self):
        # Mock Songs_Queue instance
        self.songs_cog.songs_queue = MagicMock()
        self.songs_cog.songs_queue.get_len.return_value = 0

        result = await self.songs_cog.handle_play_next(self.ctx)
        self.ctx.send.assert_called_with("❌ No more songs in the queue.")

    async def test_pause(self):
        # Test when bot is playing
        self.ctx.voice_client = MagicMock()
        self.ctx.voice_client.is_playing.return_value = True

        await self.songs_cog.pause(self.ctx)
        self.ctx.send.assert_called_with("⏸️ Paused the song.")
        self.ctx.voice_client.pause.assert_called_once()

        # Test when bot is not playing
        self.ctx.voice_client.is_playing.return_value = False
        await self.songs_cog.pause(self.ctx)
        self.ctx.send.assert_called_with(
            "❌ The bot is not playing anything at the moment."
        )

    async def test_add(self):
        # Test valid add
        query = "Test Song"
        source = "yt"
        with patch(
            "cogs.songs_cog.fetch_spotify_metadata", return_value={"track_name": "Test Song", "artist": "Test Artist"}
        ):
            await self.songs_cog.add(self.ctx, source, query=query)
            self.ctx.send.assert_called_with("✅ Added **Test Song** to the queue.")

        # Test invalid source
        source = "invalid"
        await self.songs_cog.add(self.ctx, source, query=query)
        self.ctx.send.assert_called_with("❌ Invalid source. Use 'yt', 'sc', or 'url'.")

    async def test_shuffle(self):
        # Mock Songs_Queue instance
        self.songs_cog.songs_queue = MagicMock()
        self.songs_cog.songs_queue.shuffle = MagicMock()

        await self.songs_cog.shuffle(self.ctx)
        self.songs_cog.songs_queue.shuffle.assert_called_once()
        self.ctx.send.assert_called_with("🔀 Playlist shuffled.")

    async def test_next_song(self):
        # Mock next_song function
        self.songs_cog.songs_queue = MagicMock()
        self.songs_cog.songs_queue.next_song = MagicMock(return_value=("Next Song", "Next Artist", "yt", None))

        with patch.object(self.songs_cog, "play_song") as mock_play_song:
            await self.songs_cog.next_song_command(self.ctx)
            mock_play_song.assert_called_once()
            self.ctx.send.assert_called_with("✅ Skipped to **Next Song** by *Next Artist*.")

    async def test_mood(self):
        # Test mood selection
        with patch("cogs.songs_cog.get_recommended_songs_based_on_mood", return_value=[("Mood Song", "Mood Artist", "Dataset", None)]):
            await self.songs_cog.mood_recommend(self.ctx)
            self.ctx.send.assert_called_with("🎶 Now playing: **Mood Song** by *Mood Artist*")

