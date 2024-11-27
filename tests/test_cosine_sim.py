# Rest of the imports
from unittest.mock import patch
from cogs.helpers import utils

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_retrieve_song_attributes(mock_retrieve):
    mock_retrieve.return_value = [0.5] * 22
    actual_song_attributes = utils.retrieve_song_attributes("i believe", "frankie laine")
    assert actual_song_attributes == [0.5] * 22



# For testing the cosine_similarity() method. Given two song names, should return the cosine similarity between them.
def test_cosine_similarity():
    song_name1 = "cry"
    artist_name1 = "johnnie ray"
    song_name2 = "the carioca"
    artist_name2 = "les paul"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )

    expected_cosine_similarity = 0.75044

    assert round(expected_cosine_similarity, 2) == round(
        actual_cosine_similarity, 2)


def test_not_found_song():
    song_name = "song"
    artist_name = "artist"
    actual_song_attributes = utils.retrieve_song_attributes(
        song_name, artist_name)

    expected_song_attributes = [0] * 22

    assert actual_song_attributes == expected_song_attributes


def test_retrieve_attributes_alternate():

    song_name = "Hey, Soul Sister"
    artist_name = "Train"
    expected_song_attributes = [97, 89, 67, 8, 80, 217, 19, 4, 83]

    actual_song_attributes = utils.retrieve_attributes_alternate(
        song_name, artist_name)

    assert actual_song_attributes == expected_song_attributes


def test_one_not_found_song():
    song_name1 = "song"
    artist_name1 = "artist"
    song_name2 = "the carioca"
    artist_name2 = "les paul"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )

    assert actual_cosine_similarity == 0


def test_both_not_found_song():
    song_name1 = "song"
    artist_name1 = "artist"
    song_name2 = "song"
    artist_name2 = "artist"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )

    assert actual_cosine_similarity == 0


def test_both_found_alternate():
    song_name1 = "Hey, Soul Sister"
    artist_name1 = "Train"
    song_name2 = "Baby"
    artist_name2 = "Justin Bieber"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )

    expected_cosine_similarity = 0.9886360242
    assert round(actual_cosine_similarity, 4) == round(
        expected_cosine_similarity, 4)


def test_orthagonal_vectors():
    song_name1 = "TestSong1"
    artist_name1 = "TestArtist1"
    song_name2 = "TestSong2"
    artist_name2 = "TestArtist2"

    song1 = utils.retrieve_attributes_alternate(song_name1, artist_name1)
    song2 = utils.retrieve_attributes_alternate(song_name2, artist_name2)

    expected_song1 = [1, 0, 1, 0, 1, 0, 1, 0, 1]
    expected_song2 = [0, 1, 0, 1, 0, 1, 0, 1, 0]

    assert song1 == expected_song1
    assert song2 == expected_song2

    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )

    assert actual_cosine_similarity == 0


def test_get_full_song_name():
    song_name = "Hey, Soul"
    artist_name = "Train"
    full_song_name = utils.get_full_song_name(song_name, artist_name)
    expected_song_name = "Hey, Soul Sister"
    expected_artist_name = "Train"

    assert full_song_name[0] == expected_song_name
    assert full_song_name[1] == expected_artist_name
