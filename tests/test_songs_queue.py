from cogs.helpers.songs_queue import Songs_Queue
from random import shuffle

def test_singleton():
    sq1 = Songs_Queue()
    sq1.add_to_queue([("Song1", "Artist1", "source", None)])
    sq2 = Songs_Queue()
    assert sq1 == sq2
    assert sq1.queue == sq2.queue

    sq2.clear()
    assert sq1 == sq2
    assert sq1.queue == sq2.queue


def test_current_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([("Song1", "Artist1", "source", None)])
    result = sq.current_song()
    assert result == ("Song1", "Artist1", "source", None)


def test_next_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ])
    result = sq.next_song()
    assert result == ("Song2", "Artist2", "source", None)


def test_prev_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ])
    sq.next_song()  # Advance to Song2
    result = sq.prev_song()
    assert result == ("Song1", "Artist1", "source", None)


def test_shuffle_queue():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None),
        ("Song3", "Artist3", "source", None)
    ])
    current_song = sq.current_song()
    sq.shuffle_queue()
    assert current_song in sq.queue
    assert len(sq.queue) == 3  # Queue length should remain the same.


def test_remove_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ])
    sq.remove_from_queue("Song1")
    assert sq.queue == [("Song2", "Artist2", "source", None)]


def test_move_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None),
        ("Song3", "Artist3", "source", None)
    ])
    sq.move_song("Song3", 1)  # Move "Song3" to position 1 (1-based index)
    assert sq.queue == [
        ("Song3", "Artist3", "source", None),
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ]


def test_remove_nonexistent_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ])
    result = sq.remove_from_queue("Nonexistent")
    assert result == -1


def test_queue_length():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None),
        ("Song3", "Artist3", "source", None)
    ])
    assert sq.get_len() == 3


def test_clear_queue():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([
        ("Song1", "Artist1", "source", None),
        ("Song2", "Artist2", "source", None)
    ])
    sq.clear()
    assert sq.queue == []
    assert sq.index == 0


def test_shuffle_queue_empty():
    sq = Songs_Queue()
    sq.clear()
    sq.shuffle_queue()
    assert sq.queue == []


def test_shuffle_queue_single_song():
    sq = Songs_Queue()
    sq.clear()
    sq.add_to_queue([("Song1", "Artist1", "source", None)])
    sq.shuffle_queue()
    assert sq.queue == [("Song1", "Artist1", "source", None)]
