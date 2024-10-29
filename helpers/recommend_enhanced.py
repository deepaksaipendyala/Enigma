"""
This file contains the enhanced recommendation function that uses cosine similarity to recommend songs.
"""

from helpers.utils import retrieve_song_attributes, cosine_similarity
from helpers.get_all import get_all_songs


def recommend_enhanced(input_songs: list) -> list:
    """
    This function returns recommended songs based on the songs that the user selected.
    It uses the cosine similarity to recommend songs. It will return a list of 10 songs that are the most
    similar to the input songs.

    Parameters:
        input_songs (list): List of songs that the user selected. Format as (track_name, artist_name).
    """

    # Get all songs
    all_songs = get_all_songs()

    # Iterate through all the songs and get the cosine similarity between the input songs and all the songs
    # and store it in a dictionary with the song name as the key and the cosine similarity as the value

    # Get the song attributes for the input songs
    input_song_attributes = {}
    genres = []
    for song in input_songs:
        song_name = song[0]
        artist_name = song[1]
        song_attributes = retrieve_song_attributes(song_name, artist_name)
        if song_attributes is not None:
            input_song_attributes[(song_name, artist_name)] = song_attributes

        # Get the genre of the song
        genre = all_songs.loc[
            (all_songs["track_name"] == song_name)
            & (all_songs["artist_name"] == artist_name)
        ]["genre"].values.tolist()
        if len(genre) > 0:
            genres.append(genre[0])

    # Filter the songs based on the genre of the input songs
    all_songs = all_songs[all_songs["genre"].isin(genres)]

    # Get songs that are similar genres to the input songs
    all_song_attributes = {}
    num_retrieved = 0

    # Randomize the order of the songs
    all_songs = all_songs.sample(frac=1).reset_index(drop=True)

    for index, row in all_songs.iterrows():
        song_name = row["track_name"]
        artist_name = row["artist_name"]
        song_attributes = retrieve_song_attributes(song_name, artist_name)
        if song_attributes is not None:
            num_retrieved += 1
            all_song_attributes[(song_name, artist_name)] = song_attributes

        if num_retrieved >= 500:
            break

    # Calculate the cosine similarity between the input songs and all the songs. The final similarity score
    # for each song will be the average of all the cosine similarities between the input songs and the song

    # Create a list to store the cosine similarity for each song. Will be stored in the format ((song_name, artist_name), similarity_score)
    similarity_scores = []

    for song_name, artist_name in all_song_attributes.keys():
        similarity_score = 0
        for input_song_name, input_artist_name in input_song_attributes.keys():
            similarity_score += cosine_similarity(
                song_name, artist_name, input_song_name, input_artist_name
            )

        similarity_score /= len(input_song_attributes)
        similarity_scores.append([(song_name, artist_name), similarity_score])

    # Sort the similarity scores in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # return the song name and artist name for the top 10 songs
    recommended_songs = [x[0] for x in similarity_scores[:10]]
    return recommended_songs
