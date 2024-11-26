"""
This file is responsible for handling all data operations such as showing songs that the user can select.
Recommendation of songs filtering operations etc.
"""

import pandas as pd
import random


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


def get_recommended_songs_based_on_mood(filters):
    """
    Filter the dataset based on the provided filter ranges for mood.
    The filters parameter is expected to be a dictionary with keys as feature names and values as a tuple of (min, max).
    
    Returns:
        list of tuples: Each tuple contains (track_name, artist)
    """
    import pandas as pd
    import logging

    logger = logging.getLogger(__name__)

    # Load the dataset.
    try:
        tcc_ceds_music_df = pd.read_csv('./data/tcc_ceds_music.csv')
        logger.debug("Dataset loaded successfully.")
    except FileNotFoundError:
        logger.error("Dataset file not found.")
        return []
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        return []

    # Ensure the necessary columns exist
    required_columns = {'track_name', 'artist'}
    if not required_columns.issubset(tcc_ceds_music_df.columns):
        logger.error(f"Dataset is missing required columns: {required_columns - set(tcc_ceds_music_df.columns)}")
        return []

    # Start with the dataset and filter it based on the ranges provided in the filters
    filtered_df = tcc_ceds_music_df.copy()
    logger.debug("Starting to apply filters to the dataset.")

    for feature, (min_val, max_val) in filters.items():
        if feature in filtered_df.columns:
            original_count = len(filtered_df)
            filtered_df = filtered_df[(filtered_df[feature] >= min_val) & (filtered_df[feature] <= max_val)]
            new_count = len(filtered_df)
            logger.debug(f"Applied filter on '{feature}': {original_count} -> {new_count} songs.")
        else:
            logger.warning(f"Feature '{feature}' not found in the dataset columns.")

    # If there are no results, return an empty list
    if filtered_df.empty:
        logger.info("No songs found after applying filters.")
        return []

    # Extract the 'track_name' and 'artist' as the recommended songs
    # Return as list of tuples (track_name, artist)
    recommended_songs = list(filtered_df[['track_name', 'artist']].head(20).itertuples(index=False, name=None))
    logger.info(f"Recommended {len(recommended_songs)} songs based on mood.")
    return recommended_songs
