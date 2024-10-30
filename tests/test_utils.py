import warnings
import sys
from cogs.helpers import utils
import numpy as np

sys.path.append("../")
warnings.filterwarnings("ignore")


# For testing the searchSong() method. Given a song name as input, should return the youtube link.
def test_searchSong():
    song_name = "Watermelon Sugar"
    actual_link = utils.searchSong(song_name)
    expected_link = "https://www.youtube.com/watch?v=E07s5ZYygMg"
    assert actual_link == expected_link


# For testing the random_25() method. Checking if the list returned is of length 25.


def test_random_25():
    random_songs = utils.random_25()
    assert len(random_songs) == 25


def test_random_n():
    """
    Test a function to get a number of random songs
    """
    n = 10
    random_songs = utils.random_n(n)
    assert len(random_songs) == n


def test_random_n_max():
    """
    Test a function to get a number of random songs with n = length of the larger dataset
    """
    n = len(utils.all_songs_attributes)
    random_songs = utils.random_n(n)
    assert len(random_songs) == n


def test_random_n_several_times():
    """
    Test a function to get a number of random songs with different values of n
    """

    # Test the function with a number between 1 and 500 10 times
    for i in range(10):
        n = np.random.randint(1, len(utils.all_songs_attributes))
        random_songs = utils.random_n(n)
        assert len(random_songs) == n
