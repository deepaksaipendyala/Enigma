import warnings
from cogs.helpers import get_all

warnings.filterwarnings("ignore")


def test_filtered_songs():
    filtered = get_all.filtered_songs()
    print(filtered)
    assert len(filtered) != 0


def test_get_all_songs():
    songs = get_all.get_all_songs()
    print(songs)
    assert len(songs) != 0


def test_recommend():
    ts = {"track_name": "Your Love Is My Drug", "genre": "dance pop"}
    songs = get_all.recommend(ts)
    print(songs)
    # test = {"track_name": "Living For Love", "genre": "dance pop"}
    assert len(songs) == 10
