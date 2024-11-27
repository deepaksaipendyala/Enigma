from cogs.helpers.songs_queue import Songs_Queue
import warnings
import sys

sys.path.append("../")

warnings.filterwarnings("ignore")


def test_singleton():
    songs = ["a", "b", "c", "d"]
    sq1 = Songs_Queue()
    sq1.add_to_queue(songs)
    sq2 = Songs_Queue()

    assert sq1 == sq2
    assert sq1.queue == sq2.queue

    sq2.clear()

    assert sq1 == sq2
    assert sq1.queue == sq2.queue


def test_current_song():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.current_song()
    assert "a" == result


def test_current_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.current_song()
    assert "TiK ToK" == result

    sq.remove_from_queue("TiK ToK")
    result = sq.current_song()
    assert "Baby" == result


def test_next_song():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.next_song()
    assert "b" == result


def test_next_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.next_song()
    assert "Baby" == result


def test_prev_song():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.prev_song()
    assert "d" == result


def test_prev_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.prev_song()
    assert "Secrets" == result


def test_get_len():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.get_len()
    assert 5 == result


def test_get_len_2():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.get_len()
    assert 4 == result


def test_return_queue():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.return_queue()
    expectedResult = ([("a", "Unknown"), ("b", "Unknown"),
                      ("c", "Unknown"), ("d", "Unknown")], 0)
    assert result == expectedResult


def test_return_queue_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.return_queue()
    expectedResult = ([("TiK ToK", "Unknown"), ("Baby", "Unknown"), ("Marry You",
                      "Unknown"), ("Telephone", "Unknown"), ("Secrets", "Unknown")], 0)
    assert result == expectedResult


def test_shuffle_queue():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)

    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == "TiK ToK"
    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == "TiK ToK"
    result = sq.next_song()
    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == result
    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == result
    result = sq.next_song()
    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == result
    sq.shuffle_queue()
    assert sq.queue[sq._index][0] == result


def test_move_song_1():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    sq.move_song("Secrets", 1)
    assert sq.queue == [("TiK ToK", "Unknown"), ("Secrets", "Unknown"),
                        ("Baby", "Unknown"), ("Marry You", "Unknown"), ("Telephone", "Unknown")]


def test_move_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.move_song("Secrets", 0)
    assert result == -2
    result = sq.move_song("Secrets", 5)
    assert result == -2


def test_move_song_3():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.move_song("Magic", 1)
    assert result == -1


def test_remove_song_1():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    sq.remove_from_queue("Secrets")
    assert sq.queue == [("TiK ToK", "Unknown"), ("Baby", "Unknown"),
                        ("Marry You", "Unknown"), ("Telephone", "Unknown")]
    sq.remove_from_queue("Baby")
    assert sq.queue == [("TiK ToK", "Unknown"),
                        ("Marry You", "Unknown"), ("Telephone", "Unknown")]


def test_remove_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.remove_from_queue("Magic")
    assert result == -1


def test_remove_song_3():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue(song_names)
    result = sq.remove_from_queue("TiK ToK")

    assert result == 0
    assert sq.index == 0
    assert sq.queue == [("Baby", "Unknown"), ("Marry You", "Unknown"),
                        ("Telephone", "Unknown"), ("Secrets", "Unknown")]


async def test_volume_command():
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