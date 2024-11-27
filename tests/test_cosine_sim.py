import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the required environment variables are set
if not os.getenv("SPOTIPY_CLIENT_ID") or not os.getenv("SPOTIPY_CLIENT_SECRET"):
    raise EnvironmentError("Spotify credentials are missing. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.")

# Rest of the imports
from cogs.helpers import utils


def test_retrieve_song_attributes():
    song_name = "i believe"
    artist_name = "frankie laine"
    actual_song_attributes = utils.retrieve_song_attributes(
        song_name, artist_name)
    expected_song_attributes = [
        0.0355371338259024,
        0.09677674227829695,
        0.44343517381864045,
        0.0012836971138939872,
        0.0012836970540271917,
        0.02700747737752981,
        0.0012836971498796242,
        0.0012836971222831008,
        0.0012836971144120706,
        0.11803384116823598,
        0.001283697092589732,
        0.2126810671851602,
        0.05112419901776462,
        0.0012836970563617238,
        0.0012836971300268928,
        0.0012836971751683166,
        0.33174482833315283,
        0.64753993282568,
        0.9548192317462166,
        1.5283400809716598e-06,
        0.3250206100577081,
        0.2632402533492537,
    ]

    print(len(actual_song_attributes))

    assert len(actual_song_attributes) == len(expected_song_attributes)

    for i in range(len(actual_song_attributes)):
        expected_attr = round(expected_song_attributes[i], 10)
        actual_attr = round(actual_song_attributes[i], 10)
        assert expected_attr == actual_attr


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
