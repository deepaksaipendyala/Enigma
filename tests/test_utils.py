import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from cogs.helpers import utils

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1", "Song2"] * 13}))
def test_random_25(mock_songs):
    """
    Test if `random_25` retrieves exactly 25 songs when `SONGS` dataset is populated.
    """
    random_songs = utils.random_25()
    assert len(random_songs) == 25

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1", "Song2"] * 10}))
def test_random_n(mock_songs):
    """
    Test if `random_n` retrieves the requested number of songs from `SONGS` dataset.
    """
    random_songs = utils.random_n(10)
    assert len(random_songs) == 10

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_same_song(mock_retrieve):
    mock_retrieve.return_value = [1, 0, 1]
    similarity = utils.cosine_similarity("Song1", "Artist1", "Song1", "Artist1")
    assert similarity == pytest.approx(1.0, rel=1e-9)

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_different_songs(mock_retrieve):
    mock_retrieve.side_effect = [[1, 0, 1], [0, 1, 0]]
    similarity = utils.cosine_similarity("Song1", "Artist1", "Song2", "Artist2")
    assert similarity == pytest.approx(0.0, rel=1e-9)


@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame())
def test_random_n_empty_dataset(mock_songs):
    """
    Test if `random_n` handles an empty dataset gracefully.
    """
    random_songs = utils.random_n(5)
    assert random_songs.empty

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_partial_overlap(mock_retrieve):
    """
    Test cosine similarity for songs with partially overlapping attributes.
    """
    mock_retrieve.side_effect = [[1, 1, 0], [1, 0, 1]]
    similarity = utils.cosine_similarity("Song1", "Artist1", "Song2", "Artist2")
    expected_similarity = pytest.approx(0.5, rel=1e-9)  # Pre-calculated similarity
    assert similarity == expected_similarity

@patch("cogs.helpers.utils.retrieve_song_attributes")
def test_cosine_similarity_missing_attributes(mock_retrieve):
    """
    Test cosine similarity when one or both songs have missing attributes.
    """
    mock_retrieve.side_effect = [[0] * 22, [1, 0, 1]]
    similarity = utils.cosine_similarity("Song1", "Artist1", "Song2", "Artist2")
    assert similarity == 0.0  # Similarity should be 0 due to missing attributes

@patch("cogs.helpers.utils.fetch_spotify_metadata")
def test_searchSong_with_spotify_metadata(mock_spotify):
    """
    Test `searchSong` with Spotify metadata available.
    """
    mock_spotify.return_value = {"track_name": "Song1", "artist": "Artist1"}
    youtube_url = utils.searchSong("Song1")
    assert "https://www.youtube.com" in youtube_url

@patch("cogs.helpers.utils.fetch_spotify_metadata")
def test_searchSong_no_spotify_metadata(mock_spotify):
    """
    Test `searchSong` when Spotify metadata is not available.
    """
    mock_spotify.return_value = {}
    youtube_url = utils.searchSong("Nonexistent Song")
    # Check if the result is a valid YouTube URL
    assert "https://www.youtube.com" in youtube_url

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1"], "artist": ["Artist1"]}))
def test_get_full_song_name(mock_songs):
    """
    Test `get_full_song_name` for a valid song in the dataset.
    """
    result = utils.get_full_song_name("Song1", "Artist1")
    assert result == ["Song1", "Artist1"]

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame(columns=["track_name", "artist"]))
def test_get_full_song_name_not_found(mock_songs):
    """
    Test `get_full_song_name` when the song is not found in the dataset.
    """
    result = utils.get_full_song_name("Nonexistent Song", "Nonexistent Artist")
    assert result is None

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1", "Song2"], "artist": ["Artist1", "Artist2"]}))
def test_random_n_larger_than_dataset(mock_songs):
    """
    Test `random_n` raises an error when requesting more songs than available.
    """
    with pytest.raises(ValueError):
        utils.random_n(10)  # Requesting 10 songs when only 2 exist

@patch("cogs.helpers.utils.retrieve_attributes_alternate")
def test_cosine_similarity_alternate_dataset(mock_retrieve):
    """
    Test cosine similarity using attributes from the alternate dataset.
    """
    mock_retrieve.side_effect = [[0.5] * 9, [0.5] * 9]
    similarity = utils.cosine_similarity("Song1", "Artist1", "Song2", "Artist2")
    assert similarity == pytest.approx(1.0, rel=1e-9)

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1"], "artist": ["Artist1"]}))
def test_random_n_zero(mock_songs):
    """
    Test `random_n` when requesting zero songs.
    """
    random_songs = utils.random_n(0)
    assert len(random_songs) == 0  # Should return an empty DataFrame

@patch("cogs.helpers.utils.SONGS", new_callable=lambda: pd.DataFrame({"track_name": ["Song1"], "artist": ["Artist1"]}))
def test_random_n_negative(mock_songs):
    """
    Test `random_n` when requesting a negative number of songs.
    """
    with pytest.raises(ValueError):
        utils.random_n(-5)
