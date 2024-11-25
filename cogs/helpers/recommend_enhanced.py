# cogs/helpers/recommend_enhanced.py
"""
This file contains the enhanced recommendation function that uses cosine similarity to recommend songs.
"""

from cogs.helpers.utils import retrieve_song_attributes, cosine_similarity
from cogs.helpers.get_all import get_all_songs
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

def recommend_enhanced(input_songs: list) -> list:
    """
    Returns recommended songs based on the songs that the user selected.
    It uses cosine similarity to recommend songs. It will return a list of 10 songs that are the most
    similar to the input songs.

    Parameters:
        input_songs (list): List of songs that the user selected. Format as (track_name, artist).

    Returns:
        list: List of recommended songs as tuples (track_name, artist).
    """

    # Get all songs
    all_songs = get_all_songs()

    # Iterate through all the songs and get the cosine similarity between the input songs and all the songs
    # and store it in a list with the song tuple and the similarity score

    # Get the song attributes for the input songs
    input_song_attributes = {}
    genres = []
    for song in input_songs:
        song_name, artist = song
        song_attributes = retrieve_song_attributes(song_name, artist)
        if song_attributes:
            input_song_attributes[(song_name, artist)] = song_attributes

            # Get the genre of the song
            genre_series = all_songs.loc[
                (all_songs["track_name"].str.lower() == song_name.lower()) &
                (all_songs["artist"].str.lower() == artist.lower())
            ]["genre"]
            if not genre_series.empty:
                genres.append(genre_series.iloc[0])

    if not input_song_attributes:
        logger.warning("recommend_enhanced: No valid input songs found for recommendations.")
        return []

    # Filter the songs based on the genres of the input songs
    all_songs_filtered = all_songs[all_songs["genre"].isin(genres)]

    # Get song attributes for filtered songs
    all_song_attributes = {}
    num_retrieved = 0
    max_retrieved = 500  # Limit to first 500 songs for performance

    # Randomize the order of the songs
    all_songs_filtered = all_songs_filtered.sample(frac=1).reset_index(drop=True)

    for index, row in all_songs_filtered.iterrows():
        song_name = row["track_name"]
        artist = row["artist"]
        song_attributes = retrieve_song_attributes(song_name, artist)
        if song_attributes:
            all_song_attributes[(song_name, artist)] = song_attributes
            num_retrieved += 1
        if num_retrieved >= max_retrieved:
            break

    # Calculate the cosine similarity between the input songs and all the songs
    similarity_scores = []

    for song_tuple, attributes in all_song_attributes.items():
        similarity_score = 0.0
        for input_song_tuple, input_attributes in input_song_attributes.items():
            sim = cosine_similarity(
                song_tuple[0], song_tuple[1],
                input_song_tuple[0], input_song_tuple[1]
            )
            similarity_score += sim
        similarity_score /= len(input_song_attributes)
        similarity_scores.append((song_tuple, similarity_score))

    # Sort the similarity scores in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # Return the top 10 recommended songs
    recommended_songs = [x[0] for x in similarity_scores[:10]]
    logger.info(f"recommend_enhanced: Generated {len(recommended_songs)} recommendations.")
    return recommended_songs
