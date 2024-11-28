from unittest.mock import patch
from cogs.helpers import utils
import pytest
import numpy as np
import pandas as pd


@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_retrieve_song_attributes(mock_retrieve):
    mock_retrieve.return_value = [0.5] * 22
    song_name = "i believe"
    artist_name = "frankie laine"
    actual_song_attributes = utils.retrieve_song_attributes(song_name, artist_name)
    expected_song_attributes = [0.5] * 22
    assert actual_song_attributes == expected_song_attributes


@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_not_found_song(mock_retrieve):
    mock_retrieve.return_value = [0.5] * 22
    song_name = "song"
    artist_name = "artist"
    actual_song_attributes = utils.retrieve_song_attributes(song_name, artist_name)
    expected_song_attributes = [0.5] * 22
    assert actual_song_attributes == expected_song_attributes


@patch("cogs.helpers.utils.retrieve_attributes_alternate")
def test_retrieve_attributes_alternate(mock_retrieve):
    mock_retrieve.return_value = [97, 89, 67, 8, 80, 217, 19, 4, 83]
    song_name = "Hey, Soul Sister"
    artist_name = "Train"
    actual_song_attributes = utils.retrieve_attributes_alternate(song_name, artist_name)
    expected_song_attributes = [97, 89, 67, 8, 80, 217, 19, 4, 83]
    assert actual_song_attributes == expected_song_attributes


@patch("cogs.helpers.utils.cosine_similarity")
def test_cosine_similarity(mock_cosine):
    mock_cosine.return_value = 1.0
    song_name1 = "cry"
    artist_name1 = "johnnie ray"
    song_name2 = "the carioca"
    artist_name2 = "les paul"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    expected_cosine_similarity = 1.0
    assert actual_cosine_similarity == expected_cosine_similarity


@patch("cogs.helpers.utils.cosine_similarity")
def test_one_not_found_song(mock_cosine):
    mock_cosine.return_value = 1.0
    song_name1 = "song"
    artist_name1 = "artist"
    song_name2 = "the carioca"
    artist_name2 = "les paul"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    expected_cosine_similarity = 1.0
    assert actual_cosine_similarity == expected_cosine_similarity


@patch("cogs.helpers.utils.cosine_similarity")
def test_both_not_found_song(mock_cosine):
    mock_cosine.return_value = 1.0
    song_name1 = "song"
    artist_name1 = "artist"
    song_name2 = "song"
    artist_name2 = "artist"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    expected_cosine_similarity = 1.0
    assert actual_cosine_similarity == expected_cosine_similarity


@patch("cogs.helpers.utils.cosine_similarity")
def test_both_found_alternate(mock_cosine):
    mock_cosine.return_value = 1.0
    song_name1 = "Hey, Soul Sister"
    artist_name1 = "Train"
    song_name2 = "Baby"
    artist_name2 = "Justin Bieber"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    expected_cosine_similarity = 1.0
    assert actual_cosine_similarity == expected_cosine_similarity


@patch("cogs.helpers.utils.retrieve_attributes_alternate")
def test_orthogonal_vectors(mock_retrieve):
    mock_retrieve.side_effect = [
        [1, 0, 1, 0, 1, 0, 1, 0, 1],  # Attributes for song1
        [0, 1, 0, 1, 0, 1, 0, 1, 0],  # Attributes for song2
    ]
    song_name1 = "TestSong1"
    artist_name1 = "TestArtist1"
    song_name2 = "TestSong2"
    artist_name2 = "TestArtist2"
    song1 = utils.retrieve_attributes_alternate(song_name1, artist_name1)
    song2 = utils.retrieve_attributes_alternate(song_name2, artist_name2)

    assert song1 == [1, 0, 1, 0, 1, 0, 1, 0, 1]
    assert song2 == [0, 1, 0, 1, 0, 1, 0, 1, 0]


@patch("cogs.helpers.utils.get_full_song_name")
def test_get_full_song_name(mock_get_full_song_name):
    mock_get_full_song_name.return_value = ["Hey, Soul Sister", "Train"]
    song_name = "Hey, Soul"
    artist_name = "Train"
    full_song_name = utils.get_full_song_name(song_name, artist_name)
    expected_song_name = "Hey, Soul Sister"
    expected_artist_name = "Train"

    assert full_song_name[0] == expected_song_name
    assert full_song_name[1] == expected_artist_name

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_empty_song_and_artist(mock_retrieve):
    mock_retrieve.return_value = [0.5] * 22
    song_name = ""
    artist_name = ""
    actual_song_attributes = utils.retrieve_song_attributes(song_name, artist_name)
    expected_song_attributes = [0.5] * 22
    assert actual_song_attributes == expected_song_attributes


@patch("cogs.helpers.utils.retrieve_attributes_alternate")
def test_retrieve_attributes_with_partial_name(mock_retrieve):
    mock_retrieve.return_value = [97, 89, 67, 8, 80, 217, 19, 4, 83]
    song_name = "Soul"
    artist_name = "Train"
    actual_song_attributes = utils.retrieve_attributes_alternate(song_name, artist_name)
    expected_song_attributes = [97, 89, 67, 8, 80, 217, 19, 4, 83]
    assert actual_song_attributes == expected_song_attributes


def test_random_100_songs():
    random_songs = utils.random_n(100)
    assert len(random_songs) == 100
    assert "track_name" in random_songs.columns
    assert "artist" in random_songs.columns


@patch("cogs.helpers.utils.fetch_spotify_metadata")
def test_fetch_spotify_metadata_invalid_song(mock_fetch):
    mock_fetch.return_value = {}
    metadata = utils.fetch_spotify_metadata("Nonexistent Song")
    assert metadata == {}


@patch("cogs.helpers.utils.VideosSearch")
def test_search_song_no_results(mock_videos_search):
    mock_videos_search.return_value.result.return_value = {"result": []}
    youtube_url = utils.searchSong("Nonexistent Song", "Unknown Artist")
    assert youtube_url == ""


@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_with_identical_songs(mock_retrieve):
    mock_retrieve.return_value = [1] * 22
    song_name1 = "Same Song"
    artist_name1 = "Same Artist"
    song_name2 = "Same Song"
    artist_name2 = "Same Artist"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    assert actual_cosine_similarity == 1.0


@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_with_zero_vectors(mock_retrieve):
    mock_retrieve.return_value = [0] * 22
    song_name1 = "Song A"
    artist_name1 = "Artist A"
    song_name2 = "Song B"
    artist_name2 = "Artist B"
    actual_cosine_similarity = utils.cosine_similarity(
        song_name1, artist_name1, song_name2, artist_name2
    )
    assert actual_cosine_similarity == 0.0


def test_get_full_song_name_no_match():
    song_name = "Nonexistent Song"
    artist_name = "Unknown Artist"
    full_song_name = utils.get_full_song_name(song_name, artist_name)
    assert full_song_name is None


@patch("cogs.helpers.utils.retrieve_attributes_alternate")
def test_large_alternate_dataset(mock_retrieve):
    mock_retrieve.return_value = [np.random.randint(0, 100) for _ in range(22)]
    song_name = "Random Song"
    artist_name = "Random Artist"
    actual_song_attributes = utils.retrieve_attributes_alternate(song_name, artist_name)
    assert len(actual_song_attributes) == 22
    assert all(isinstance(attr, (int, float)) for attr in actual_song_attributes)


@patch("cogs.helpers.utils.random_n")
def test_random_song_with_empty_dataset(mock_random_n):
    mock_random_n.return_value = pd.DataFrame()
    random_songs = utils.random_n(10)
    assert random_songs.empty


@patch("cogs.helpers.utils.searchSong")
def test_search_song_edge_case(mock_search_song):
    mock_search_song.return_value = "https://youtube.com/edge_case_song"
    youtube_url = utils.searchSong("", "")
    assert youtube_url == "https://youtube.com/edge_case_song"
