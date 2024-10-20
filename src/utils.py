"""
This file is responsible for all the helper functions that are used
"""
from youtubesearchpython import VideosSearch
from src.get_all import filtered_songs, get_all_songs, get_all_songs_alternate
import numpy as np



def searchSong(name_song):
    """
    This function seaches the song on youtube and returns the URL
    """

    videosSearch = VideosSearch(name_song, limit=1)
    result = videosSearch.result()
    link = result['result'][0]['link']
    return link


all_songs = filtered_songs()[["track_name", "artist", "genre"]]



def random_25():
    """
    This function returns random 25 songs for generating the poll for the user
    """

    random_songs = (all_songs.sample(
        frac=1).groupby('genre').head(1)).sample(25)
    return random_songs


def retrieve_song_attributes(songName, artistName):
    """
    This function returns the attributes of the song
    """
    try:

        # Get the song attributes from the all_songs dataframe
        all_songs = get_all_songs().filter(["artist_name","track_name","dating","violence","world/life","night/time","shake the audience","family/gospel","romantic","communication","obscene","music","movement/places","light/visual perceptions","family/spiritual",'like/girls',"sadness","feelings","danceability","loudness","acousticness","instrumentalness","valence","energy"])

        # Get the attributes of the song
        song = all_songs.loc[(all_songs["track_name"] == songName) & (all_songs["artist_name"] == artistName)]

        song_attributes = song.values.tolist()[0]
        # Return the attributes
        return song_attributes[2:]

    except:
        return [0]*22


def retrieve_attributes_alternate(songName, artistName):
    """
    This function will retrieve the attributes of the song from the alternate dataset, in the event
    that the song is not found in the main dataset
    """

    # Get the songs from the alternate dataset
    all_songs_alt = get_all_songs_alternate().filter(["track_name", "artist", "bpm", "nrgy", "dnce", "live", "val", "dur", "acous", "spch", "pop"])

    # Get the attributes of the song
    song = all_songs_alt.loc[(all_songs_alt["track_name"] == songName) & (all_songs_alt["artist"] == artistName)]

    # Return the attributes
    return song.values.tolist()[0][2:]


def cosine_similarity(songName1, artistName1, songName2, artistName2):
    """
    This function returns the cosine similarity between two vectors, in this case the attributes of the songs
    """

    # Get the attributes of the songs
    song1 = retrieve_song_attributes(songName1, artistName1)
    song2 = retrieve_song_attributes(songName2, artistName2)

    # Calculate the cosine similarity
    cos_sim = np.dot(song1, song2) / (np.linalg.norm(song1) * np.linalg.norm(song2))

    return cos_sim

