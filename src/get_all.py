"""
This file is responsible for handling all data operations such as showing songs that the user can select.
Recommendation of songs filtering operations etc.
"""

import pandas as pd
import random
from src.utils import retrieve_song_attributes


def filtered_songs():
    """
    This function returns songs and their track_name, artist, year and genre.
    """
    
    all_songs = pd.read_csv("./data/songs.csv")
    all_songs = all_songs.filter(["track_name", "artist", "year", "genre"])
    return all_songs


def get_all_songs():
    """
    This function returns all songs in the dataset. Uses tcc_ceds_music.csv
    """

    all_songs = pd.read_csv("./data/tcc_ceds_music.csv")
    return all_songs


def get_all_songs_alternate():
    """
    This function returns all songs in the alternate dataset. Uses songs.csv
    """

    all_songs = pd.read_csv("./data/songs.csv")
    return all_songs


def recommend(input_songs):
    """
    This function returns recommended songs based on the songs that the user selected.
    """

    # removing all songs with count = 1
    songs = get_all_songs()
    songs = songs.groupby('genre').filter(lambda x: len(x) > 0)
    # creating dictionary of song track_names and genre
    playlist = dict(zip(songs['track_name'], songs['genre']))
    # creating dictionary to count the frequency of each genre
    freq = {}
    for item in songs['genre']:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
    # create list of all songs from the input genre
    selected_list = []
    output = []
    for input in input_songs:
        if input in playlist.keys():
            for key, value in playlist.items():
                if playlist[input] == value:
                    selected_list.append(key)
            selected_list.remove(input)
    if (len(selected_list) >= 10):
        output = random.sample(selected_list, 10)
    else:
        extra_songs = 10 - len(selected_list)
        song_names = songs['track_name'].to_list()
        song_names_filtered = [x for x in song_names if x not in selected_list]
        selected_list.extend(random.sample(song_names_filtered, extra_songs))
        output = selected_list.copy()
    return output


def recommend_enchanced(input_songs):
    """
    This function returns recommended songs based on the songs that the user selected.
    It uses the cosine similarity to recommend songs. It will return a list of 10 songs that are the most
    similar to the input songs.

    Parameters:
        input_songs (list): List of songs that the user selected. Each song is a tuple with the song name and the artist name.
    """

    # Get all songs
    all_songs = get_all_songs()

    # Iterate through all the songs and get the cosine similarity between the input songs and all the songs
    # and store it in a dictionary with the song name as the key and the cosine similarity as the value    

    # Get the song attributes for the input songs
    input_song_attributes = {}
    for song in input_songs:
        song_name = song[0]
        artist_name = song[1]
        song_attributes = retrieve_song_attributes(song_name, artist_name)
        if song_attributes is not None:
            input_song_attributes[[song_name, artist_name]] = song_attributes
    
    # Get the song attributes for all the songs
    all_song_attributes = {}
    for index, row in all_songs.iterrows():
        song_name = row["track_name"]
        artist_name = row["artist_name"]
        song_attributes = retrieve_song_attributes(song_name, artist_name)
        if song_attributes is not None:
            all_song_attributes[[song_name, artist_name]] = song_attributes

    # Calculate the cosine similarity between the input songs and all the songs. The final similarity score 
    # for each song will be the average of all the cosine similarities between the input songs and the song

    # Create a list to store the cosine similarity for each song. Will be stored in the format ((song_name, artist_name), similarity_score)
    similarity_scores = []

    for song_name, artist_name in all_song_attributes.keys():
        similarity_score = 0
        for input_song_name, input_artist_name in input_song_attributes.keys():
            input_song_attributes = input_song_attributes[[input_song_name, input_artist_name]]
            all_song_attributes = all_song_attributes[[song_name, artist_name]]
            cosine_similarity = cosine_similarity(input_song_attributes, all_song_attributes)
            similarity_score += cosine_similarity
        
        similarity_score /= len(input_song_attributes)
        similarity_scores.append([[song_name, artist_name], similarity_score])
