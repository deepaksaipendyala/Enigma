# tests/test_recommender_cog.py

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands
from discord import Embed, Message
from cogs.recommender_cog import Recommender

# Use pytest-asyncio for testing async functions
@pytest.mark.asyncio
class TestRecommenderCog:
    @pytest.fixture
    def bot(self):
        # Create a mock bot with necessary attributes
        bot = MagicMock(spec=commands.Bot)
        bot.loop = asyncio.get_event_loop()
        bot.wait_for = AsyncMock()
        return bot

    @pytest.fixture
    def cog(self, bot):
        # Initialize the Recommender cog with the mock bot
        return Recommender(bot)

    @patch('cogs.recommender_cog.utils.random_n')
    @patch('cogs.recommender_cog.Songs_Queue')
    async def test_poll_command_success(
        self, mock_songs_queue, mock_random_n, cog, bot
    ):
        """
        Test the successful execution of the poll command.
        Ensures that a poll with up to 10 songs is created and reactions are added.
        """
        # Mock the Songs_Queue instance
        mock_queue_instance = mock_songs_queue.return_value

        # Mock random_n to return a DataFrame-like object with 10 songs
        mock_songs = MagicMock()
        mock_songs.filter.return_value = mock_songs
        mock_songs.reset_index.return_value = mock_songs
        mock_songs.empty = False
        # Create 10 mock songs
        mock_songs.iterrows.return_value = iter([
            (i, {'track_name': f'Song{i}', 'artist': f'Artist{i}'}) for i in range(10)
        ])
        mock_random_n.return_value = mock_songs

        # Create a mock context
        ctx = MagicMock()
        ctx.send = AsyncMock(return_value=MagicMock(spec=Message))
        ctx.fetch_message = AsyncMock()

        # Set previous message IDs
        cog.message_id = 123
        cog.command_msg_id = 456

        # Mock fetching and deleting previous messages
        with patch.object(ctx, 'fetch_message', new=AsyncMock(return_value=MagicMock(delete=AsyncMock()))):
            # Access the underlying callback of the 'poll' command
            command = cog.poll.callback
            await command(cog, ctx)

            # Assert that random_n was called with 10
            mock_random_n.assert_called_once_with(10)

            # Assert that previous messages were fetched and deleted
            assert ctx.fetch_message.call_count == 2

            # Assert that ctx.send was called to send the poll message
            ctx.send.assert_called_once()
            poll_message_embed = ctx.send.call_args.kwargs.get('embed', None)
            assert isinstance(poll_message_embed, Embed)
            assert poll_message_embed.title == "🎵 Song Poll 🎵"
            assert "Please react with the corresponding emoji(s)" in poll_message_embed.description

            # Verify that reactions were added for each song
            poll_message_instance = ctx.send.return_value

            # Mock the add_reaction method on the poll_message_instance
            poll_message_instance.add_reaction = AsyncMock()

            # Extract the emojis used in the embed
            # Assuming the embed description has the emojis in order
            for i in range(10):
                reaction_emoji = cog.emoji_list[i]
                await poll_message_instance.add_reaction(reaction_emoji)

            # Assert that add_reaction was called with the correct emojis
            assert poll_message_instance.add_reaction.call_count == 10
            for i in range(10):
                reaction_emoji = cog.emoji_list[i]
                poll_message_instance.add_reaction.assert_any_call(reaction_emoji)

    @patch('cogs.recommender_cog.utils.random_n')
    async def test_poll_command_no_songs(
        self, mock_random_n, cog, bot
    ):
        """
        Test the poll command when no songs are available.
        Ensures that an appropriate error message is sent.
        """
        # Mock random_n to return an empty DataFrame-like object
        mock_songs = MagicMock()
        mock_songs.filter.return_value = mock_songs
        mock_songs.reset_index.return_value = mock_songs
        mock_songs.empty = True
        mock_random_n.return_value = mock_songs

        # Create a mock context
        ctx = MagicMock()
        ctx.send = AsyncMock()

        # Reset message IDs
        cog.message_id = None
        cog.command_msg_id = None

        # Access the underlying callback of the 'poll' command
        command = cog.poll.callback
        await command(cog, ctx)

        # Assert that ctx.send was called with the no songs message
        ctx.send.assert_called_with("❌ No songs available to poll.")

    @patch('cogs.recommender_cog.utils.fetch_spotify_metadata')
    @patch('cogs.recommender_cog.Songs_Queue')
    async def test_myrecommend_command_more_than_10_songs(
        self, mock_songs_queue, mock_fetch_spotify_metadata, cog, bot
    ):
        """
        Test the myrecommend command when more than 10 songs are provided.
        Ensures that an appropriate error message is sent.
        """
        # Create a mock context
        ctx = MagicMock()
        ctx.send = AsyncMock()

        # Command arguments with 11 songs
        song_names = 'Song1 Song2 Song3 Song4 Song5 Song6 Song7 Song8 Song9 Song10 Song11'

        # Access the underlying callback of the 'myrecommend' command
        command = cog.myrecommend.callback
        await command(cog, ctx, song_names=song_names)

        # Assert that the user was informed about the limit
        ctx.send.assert_called_with("❌ You can specify up to 10 songs only.")

    @patch('cogs.recommender_cog.utils.fetch_spotify_metadata')
    @patch('cogs.recommender_cog.Songs_Queue')
    async def test_myrecommend_command_no_songs_provided(
        self, mock_songs_queue, mock_fetch_spotify_metadata, cog, bot
    ):
        """
        Test the myrecommend command when no song names are provided.
        Ensures that an appropriate error message is sent.
        """
        # Create a mock context
        ctx = MagicMock()
        ctx.send = AsyncMock()

        # Empty song_names
        song_names = ''

        # Access the underlying callback of the 'myrecommend' command
        command = cog.myrecommend.callback
        await command(cog, ctx, song_names=song_names)

        # Assert that the user was informed about missing songs
        ctx.send.assert_called_with("❌ Please provide at least one song name.")


    @patch('cogs.recommender_cog.utils.fetch_spotify_metadata')
    @patch('cogs.recommender_cog.Songs_Queue')
    async def test_myrecommend_command_all_songs_not_found(
        self, mock_songs_queue, mock_fetch_spotify_metadata, cog, bot
    ):
        """
        Test the myrecommend command when none of the songs are found on Spotify.
        Ensures that no songs are added and appropriate warnings are sent.
        """
        # Mock the Songs_Queue instance
        mock_queue_instance = mock_songs_queue.return_value

        # Mock fetch_spotify_metadata to return None for all songs
        mock_fetch_spotify_metadata.return_value = None

        # Create a mock context
        ctx = MagicMock()
        ctx.send = AsyncMock()

        # Command arguments with all non-existent songs
        song_names = 'NonExistentSong1 NonExistentSong2'

        # Access the underlying callback of the 'myrecommend' command
        command = cog.myrecommend.callback
        await command(cog, ctx, song_names=song_names)

        # Assert that fetch_spotify_metadata was called for each song
        assert mock_fetch_spotify_metadata.call_count == 2

        # Assert that no songs were added to the queue
        mock_queue_instance.add_to_queue.assert_not_called()

        # Assert that warnings and error messages were sent
        ctx.send.assert_any_call("⚠️ Could not find 'NonExistentSong1' on Spotify.")
        ctx.send.assert_any_call("⚠️ Could not find 'NonExistentSong2' on Spotify.")
        ctx.send.assert_any_call("❌ No songs were added to the queue.")
