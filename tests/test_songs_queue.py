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
    assert "b" == result


def test_next_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    ts = [song_names]
    result = sq.next_song()
    assert "Baby" == result


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
    expectedResult = (song_names, 0)
    assert result == expectedResult


def test_return_queue_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    result = sq.return_queue()
    expectedResult = (song_names, 0)
    assert result == expectedResult

def test_shuffle_queue():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == "TiK ToK"
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == "TiK ToK"
    result = sq.next_song()
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == result
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == result
    result = sq.next_song()
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == result
    sq.shuffle_queue()
    assert sq.queue[sq.current_index] == result

def test_move_song_1():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    sq.move_song("Secrets", 1)
    assert sq.queue == ["TiK ToK", "Secrets", "Baby", "Marry You", "Telephone"]

def test_move_song_2():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    result = sq.move_song("Secrets", 0)
    assert result == -2
    result = sq.move_song("Secrets", 5)
    assert result == -2

def test_move_song_3():
    song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
    sq = Songs_Queue(song_names)
    result = sq.move_song("Magic", 1)
    assert result == -1
