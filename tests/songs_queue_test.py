import unittest
import warnings
import sys

sys.path.append("../")
from cogs.helpers.songs_queue import Songs_Queue

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):

    def test_next_song(self):
        song_names = ["a", "b", "c", "d"]
        sq = Songs_Queue(song_names)
        ts = [song_names]
        function = sq.next_song()
        self.assertTrue("a" == function)

    def test_next_song_2(self):
        song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
        sq = Songs_Queue(song_names)
        ts = [song_names]
        function = sq.next_song()
        self.assertTrue("TiK ToK" == function)

    def test_prev_song(self):
        song_names = ["a", "b", "c", "d"]
        sq = Songs_Queue(song_names)
        ts = [song_names]
        function = sq.prev_song()
        self.assertTrue("d" == function)

    def test_prev_song_2(self):
        song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
        sq = Songs_Queue(song_names)
        ts = [song_names]
        function = sq.prev_song()
        self.assertTrue("Secrets" == function)

    def test_get_len(self):
        song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
        sq = Songs_Queue(song_names)
        function = sq.get_len()
        self.assertTrue(5 == function)

    def test_get_len(self):
        song_names = ["a", "b", "c", "d"]
        sq = Songs_Queue(song_names)
        function = sq.get_len()
        self.assertTrue(4 == function)

    def test_return_queue(self):
        song_names = ["a", "b", "c", "d"]
        sq = Songs_Queue(song_names)
        function = sq.return_queue()
        result = (song_names, 0)
        self.assertTrue(result == function)

    def test_return_queue_2(self):
        song_names = ["TiK ToK", "Baby", "Marry You", "Telephone", "Secrets"]
        sq = Songs_Queue(song_names)
        function = sq.return_queue()
        result = (song_names, 0)
        self.assertTrue(result == function)
