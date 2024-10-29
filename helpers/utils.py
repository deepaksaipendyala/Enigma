"""
This file is responsible for all the helper functions that are used
"""

from youtubesearchpython import VideosSearch
from helpers.get_all import filtered_songs, get_all_songs, get_all_songs_alternate
import numpy as np


def searchSong(name_song):
    """
    This function seaches the song on youtube and returns the URL
    """

    videosSearch = VideosSearch(name_song, limit=1)
    result = videosSearch.result()
    link = result["result"][0]["link"]
    return link


all_songs = filtered_songs()[["track_name", "artist", "genre"]]


def random_25():
    """
    This function returns random 25 songs for generating the poll for the user
    """

    random_songs = (all_songs.sample(frac=1).groupby("genre").head(1)).sample(25)
    return random_songs

def random_n(n: int):
    """
    This function returns random n songs for generating the poll for the user
    """
    songs = get_all_songs()
    random_songs = (songs.sample(frac=1).reset_index(drop=True)).sample(n)
    return random_songs


all_songs_attributes = get_all_songs().filter(
    [
        "artist_name",
        "track_name",
        "dating",
        "violence",
        "world/life",
        "night/time",
        "shake the audience",
        "family/gospel",
        "romantic",
        "communication",
        "obscene",
        "music",
        "movement/places",
        "light/visual perceptions",
        "family/spiritual",
        "like/girls",
        "sadness",
        "feelings",
        "danceability",
        "loudness",
        "acousticness",
        "instrumentalness",
        "valence",
        "energy",
    ]
)
all_songs_attr_alt = get_all_songs_alternate().filter(
    [
        "track_name",
        "artist",
        "bpm",
        "nrgy",
        "dnce",
        "live",
        "val",
        "dur",
        "acous",
        "spch",
        "pop",
    ]
)


def get_full_song_name(song_name, artist_name):
    """
    This function returns the full song name, when given the artist and partial song name.
    It will first search the primary dataset, and if the song is not found, it will search the alternate dataset

    Parameters:
        song_name (str): The partial name of the song
        artist_name (str): The name of the artist
    """

    # Get the songs from the primary dataset
    all_songs = get_all_songs().filter(["artist_name", "track_name"])

    # Get the song
    song = all_songs.loc[
        (all_songs["track_name"].str.contains(song_name, case=False))
        & (all_songs["artist_name"].str.contains(artist_name, case=False))
    ]

    if song.empty:
        # If the song is not found in the primary dataset, search the alternate dataset
        all_songs_alt = get_all_songs_alternate().filter(["track_name", "artist"])

        song = all_songs_alt.loc[
            (all_songs_alt["track_name"].str.contains(song_name, case=False))
            & (all_songs_alt["artist"].str.contains(artist_name, case=False))
        ]

    # If the song is not found in the alternate dataset, return None
    if song.empty:
        return None

    # Otherwise, just return the first song found

    song_name = song["track_name"].values.tolist()[0]
    artist_name = song["artist"].values.tolist()[0]
    return [song_name, artist_name]


def retrieve_song_attributes(songName, artistName):
    """
    This function returns the attributes of the song

    Parameters:
        songName (str): The name of the song
        artistName (str): The name of the artist
    """
    try:

        # Get the song attributes from the all_songs dataframe
        all_songs = all_songs_attributes

        # Get the attributes of the song
        song = all_songs.loc[
            (all_songs["track_name"] == songName)
            & (all_songs["artist_name"] == artistName)
        ]

        song_attributes = song.values.tolist()[0]
        # Return the attributes
        return song_attributes[2:]

    except:
        return [0] * 22


def retrieve_attributes_alternate(songName, artistName):
    """
    This function will retrieve the attributes of the song from the alternate dataset, in the event
    that the song is not found in the main dataset

    Parameters:
        songName (str): The name of the song
        artistName (str): The name of the artist
    """

    try:
        # Get the songs from the alternate dataset
        all_songs_alt = all_songs_attr_alt

        # Get the attributes of the song
        song = all_songs_alt.loc[
            (all_songs_alt["track_name"] == songName)
            & (all_songs_alt["artist"] == artistName)
        ]

        # Return the attributes
        return song.values.tolist()[0][2:]

    except:
        return [0] * 9


def cosine_similarity(songName1, artistName1, songName2, artistName2):
    """
    This function returns the cosine similarity between two vectors, in this case the attributes of the songs

    Parameters:
        songName1 (str): The name of the first song
        artistName1 (str): The name of the artist of the first song
        songName2 (str): The name of the second song
        artistName2 (str): The name of the artist of the second song
    """

    # Get the attributes of the songs
    song1 = retrieve_song_attributes(songName1, artistName1)
    song2 = retrieve_song_attributes(songName2, artistName2)

    if song1 == [0] * 22 or song2 == [0] * 22:
        # Try to get both the songs from the alternate dataset
        song1 = retrieve_attributes_alternate(songName1, artistName1)
        song2 = retrieve_attributes_alternate(songName2, artistName2)

        if song1 == [0] * 9 or song2 == [0] * 9:
            # If the song is not found in the alternate dataset, return 0
            return 0

        # Songs were found in the alternate dataset, we can get the cosine similarity

    # First get the dot product of the two vectors
    dot = np.dot(song1, song2)

    # Get the magnitude of the two vectors
    mag1 = np.linalg.norm(song1)
    mag2 = np.linalg.norm(song2)

    # Get the cosine similarity
    cos_sim = dot / (mag1 * mag2)

    return cos_sim
