import warnings
import sys

sys.path.append("../")
from cogs.helpers.songs_queue import Songs_Queue

warnings.filterwarnings("ignore")


def test_next_song():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue(song_names)
    ts = [song_names]
    result = sq.next_song()
    assert "a" == result


def test_next_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    ts = [song_names]
    result = sq.next_song()
    assert "TiK ToK" == result


def test_prev_song():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue(song_names)
    ts = [song_names]
    result = sq.prev_song()
    assert "d" == result


def test_prev_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    ts = [song_names]
    result = sq.prev_song()
    assert "Secrets" == result


def test_get_len():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    result = sq.get_len()
    assert 5 == result


def test_get_len():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue(song_names)
    result = sq.get_len()
    assert 4 == result


def test_return_queue():
    song_names = ["a", "b", "c", "d"]
    sq = Songs_Queue(song_names)
    result = sq.return_queue()
    result = (song_names, 0)
    assert result == result


def test_return_queue_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    result = sq.return_queue()
    result = (song_names, 0)
    assert result == result
