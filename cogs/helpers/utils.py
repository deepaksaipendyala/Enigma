# cogs/helpers/utils.py
"""
This file is responsible for all the helper functions that are used.
"""

import os
import logging
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
from cogs.helpers.get_all import filtered_songs, get_all_songs, get_all_songs_alternate
import numpy as np
import pandas as pd
from typing import Tuple, List, Union
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")

# Spotify API Setup with default fallback values for testing
client_id = os.getenv("SPOTIPY_CLIENT_ID", "test_client_id")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET", "test_client_secret")

if client_id == "test_client_id" or client_secret == "test_client_secret":
    logging.warning("Using default Spotify client credentials. Ensure actual credentials are set for production.")

spotify_auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

# Define the data directory
DATA_DIR = os.getenv("DATA_DIR", "./data")  # Default to ./data if DATA_DIR not set

def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads and preprocesses datasets, ensuring consistent column names.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: SONGS and TCC_CEDS_MUSIC DataFrames.
    """
    try:
        # Load primary dataset: songs.csv
        SONGS = pd.read_csv(os.path.join(DATA_DIR, 'songs.csv'))
        SONGS.rename(columns={'artist': 'artist'}, inplace=True)
        SONGS = SONGS[['track_name', 'artist', 'genre', 'year', 'bpm', 'nrgy', 'dnce', 'dB', 'live', 'val', 'dur', 'acous', 'spch', 'pop']]
        SONGS['track_name'] = SONGS['track_name'].str.strip()
        SONGS['artist'] = SONGS['artist'].str.strip()
        # logger.info(f"SONGS DataFrame loaded with columns: {SONGS.columns.tolist()}")
    except FileNotFoundError:
        SONGS = pd.DataFrame(columns=['track_name', 'artist', 'genre', 'year', 'bpm', 'nrgy', 'dnce', 'dB', 'live', 'val', 'dur', 'acous', 'spch', 'pop'])
        logger.error("songs.csv not found. SONGS dataset is empty.")

    try:
        # Load alternative dataset: tcc_ceds_music.csv
        TCC_CEDS_MUSIC = pd.read_csv(os.path.join(DATA_DIR, 'tcc_ceds_music.csv'))
        # Ensure correct columns are present
        if 'artist' in TCC_CEDS_MUSIC.columns:
            TCC_CEDS_MUSIC.rename(columns={'artist': 'artist'}, inplace=True)
        TCC_CEDS_MUSIC = TCC_CEDS_MUSIC[['track_name', 'artist', 'release_date', 'genre', 'lyrics', 'len', 'dating', 'violence', 'world/life', 'night/time', 'shake the audience', 'family/gospel', 'romantic', 'communication', 'obscene', 'music', 'movement/places', 'light/visual perceptions', 'family/spiritual', 'like/girls', 'sadness', 'feelings', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'topic', 'age']]
        # logger.info(f"TCC_CEDS_MUSIC DataFrame loaded with columns: {TCC_CEDS_MUSIC.columns.tolist()}")
    except FileNotFoundError:
        TCC_CEDS_MUSIC = pd.DataFrame(columns=['track_name', 'artist', 'release_date', 'genre', 'lyrics', 'len', 'dating', 'violence', 'world/life', 'night/time', 'shake the audience', 'family/gospel', 'romantic', 'communication', 'obscene', 'music', 'movement/places', 'light/visual perceptions', 'family/spiritual', 'like/girls', 'sadness', 'feelings', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'topic', 'age'])
        logger.error("tcc_ceds_music.csv not found. TCC_CEDS_MUSIC dataset is empty.")

    return SONGS, TCC_CEDS_MUSIC

# Initialize datasets
SONGS, TCC_CEDS_MUSIC = load_datasets()

def fetch_spotify_metadata(track_name: str) -> dict:
    """
    Fetches metadata for a given track from Spotify using spotipy.

    Parameters:
        track_name (str): The name of the track.

    Returns:
        dict: A dictionary containing track metadata.
    """
    results = spotify.search(q=f"track:{track_name}", type='track', limit=1)
    tracks = results.get('tracks', {}).get('items', [])
    if not tracks:
        logger.warning(f"No Spotify results found for '{track_name}'.")
        return {}

    song = tracks[0]
    metadata = {
        'track_name': song['name'],
        'artist': ', '.join([artist['name'] for artist in song['artists']]),
        'album': song['album']['name'],
        'release_date': song['album']['release_date'],
        'duration_ms': song['duration_ms'],
        'popularity': song['popularity'],
        'external_url': song['external_urls']['spotify'],
        # Add more attributes if needed
    }
    return metadata

def searchSong(name_song: str, artist: str = "") -> str:
    """
    Searches for a song on YouTube based on Spotify metadata and returns the URL.

    Parameters:
        name_song (str): The name of the song.
        artist (str): The name of the artist (optional).

    Returns:
        str: YouTube URL of the song.
    """
    if artist:
        query = f"{name_song} {artist}"
    else:
        # Fetch Spotify metadata
        metadata = fetch_spotify_metadata(name_song)
        if not metadata:
            # Fallback to using the original song name
            query = name_song
        else:
            # Use Spotify metadata to form a better query
            query = f"{metadata['track_name']} {metadata['artist']}"

    videosSearch = VideosSearch(query, limit=1)
    result = videosSearch.result()
    if result['result']:
        link = result["result"][0]["link"]
        logger.debug(f"searchSong: Found YouTube URL {link} for '{name_song}'.")
        return link
    else:
        logger.warning(f"No YouTube results found for query: {query}")
        return ""

def get_full_song_name(song_name: str, artist: str) -> Union[List[str], None]:
    """
    Returns the full song name and artist name by searching in the primary and alternate datasets.

    Parameters:
        song_name (str): Partial or full name of the song.
        artist (str): Name of the artist.

    Returns:
        list or None: [full_song_name, full_artist] or None if not found.
    """
    # Search in primary dataset
    song = SONGS.loc[
        (SONGS["track_name"].str.contains(song_name, case=False, na=False)) &
        (SONGS["artist"].str.contains(artist, case=False, na=False))
    ]

    if song.empty:
        # Search in alternate dataset
        song = TCC_CEDS_MUSIC.loc[
            (TCC_CEDS_MUSIC["track_name"].str.contains(song_name, case=False, na=False)) &
            (TCC_CEDS_MUSIC["artist"].str.contains(artist, case=False, na=False))
        ]

    if song.empty:
        logger.warning(f"Song '{song_name}' by '{artist}' not found in datasets.")
        return None

    # Return the first match
    full_song_name = song.iloc[0]['track_name']
    full_artist = song.iloc[0]['artist']
    return [full_song_name, full_artist]

def retrieve_song_attributes(songName: str, artistName: str) -> List[float]:
    """
    Retrieves attributes of a song using Spotify metadata.

    Parameters:
        songName (str): The name of the song.
        artistName (str): The name of the artist.

    Returns:
        list: A list of attributes for the song.
    """
    # For this example, we'll return dummy attributes
    # In a real implementation, you would fetch audio features from Spotify
    return [0.5] * 22  # Replace with actual attributes

def retrieve_attributes_alternate(songName: str, artistName: str) -> List[float]:
    """
    Retrieves the attributes of the song from the alternate dataset if not found in the primary dataset.

    Parameters:
        songName (str): The name of the song.
        artistName (str): The name of the artist.

    Returns:
        list: A list of attributes from the alternate dataset.
    """
    try:
        # Get the songs from the alternate dataset
        all_songs_alt = get_all_songs_alternate()

        # Get the attributes of the song
        song = all_songs_alt.loc[
            (all_songs_alt["track_name"].str.lower() == songName.lower()) &
            (all_songs_alt["artist"].str.lower() == artistName.lower())
        ]

        if song.empty:
            logger.warning(f"Song '{songName}' by '{artistName}' not found in alternate dataset.")
            return [0] * 9

        # Return the attributes
        return song.iloc[0][2:].tolist()
    except Exception as e:
        logger.error(f"Error retrieving attributes from alternate dataset: {e}")
        return [0] * 9

def cosine_similarity(songName1: str, artistName1: str, songName2: str, artistName2: str) -> float:
    """
    Returns the cosine similarity between two songs based on their attributes.

    Parameters:
        songName1 (str): The name of the first song.
        artistName1 (str): The name of the artist of the first song.
        songName2 (str): The name of the second song.
        artistName2 (str): The name of the artist of the second song.

    Returns:
        float: Cosine similarity score.
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
            return 0.0

    # Convert lists to numpy arrays
    vector1 = np.array(song1)
    vector2 = np.array(song2)

    # Calculate cosine similarity
    dot_product = np.dot(vector1, vector2)
    magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
    if magnitude == 0:
        return 0.0
    cos_sim = dot_product / magnitude

    return cos_sim

def random_n(n: int) -> pd.DataFrame:
    """
    Returns n random songs from the SONGS dataset.

    Parameters:
        n (int): Number of songs to retrieve.

    Returns:
        pd.DataFrame: DataFrame containing n random songs.
    """
    if SONGS.empty:
        logger.warning("random_n: SONGS dataset is empty.")
        return pd.DataFrame()
    return SONGS.sample(n=n).reset_index(drop=True)

def random_25() -> pd.DataFrame:
    """
    Returns 25 random songs from the SONGS dataset.

    Returns:
        pd.DataFrame: DataFrame containing 25 random songs.
    """
    return random_n(25)