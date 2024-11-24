# cogs/helpers/utils.py
"""
This file is responsible for all the helper functions that are used.
"""

import os
import logging
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from cogs.helpers.get_all import filtered_songs, get_all_songs, get_all_songs_alternate
import numpy as np
import pandas as pd
from typing import Tuple, List, Union

# Initialize Logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")

# Spotify API Setup
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)
spotify = Spotify(client_credentials_manager=client_credentials_manager)

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
        SONGS.rename(columns={'artist': 'artist_name'}, inplace=True)
        SONGS = SONGS[['track_name', 'artist_name', 'genre', 'year', 'bpm', 'nrgy', 'dnce', 'dB', 'live', 'val', 'dur', 'acous', 'spch', 'pop']]
        SONGS['track_name'] = SONGS['track_name'].str.strip()
        SONGS['artist_name'] = SONGS['artist_name'].str.strip()
        logger.info(f"SONGS DataFrame loaded with columns: {SONGS.columns.tolist()}")
    except FileNotFoundError:
        SONGS = pd.DataFrame(columns=['track_name', 'artist_name', 'genre', 'year', 'bpm', 'nrgy', 'dnce', 'dB', 'live', 'val', 'dur', 'acous', 'spch', 'pop'])
        logger.error("songs.csv not found. SONGS dataset is empty.")

    try:
        # Load alternative dataset: tcc_ceds_music.csv
        TCC_CEDS_MUSIC = pd.read_csv(os.path.join(DATA_DIR, 'tcc_ceds_music.csv'))
        # Ensure correct columns are present
        if 'artist' in TCC_CEDS_MUSIC.columns:
            TCC_CEDS_MUSIC.rename(columns={'artist': 'artist_name'}, inplace=True)
        TCC_CEDS_MUSIC = TCC_CEDS_MUSIC[['track_name', 'artist_name', 'release_date', 'genre', 'lyrics', 'len', 'dating', 'violence', 'world/life', 'night/time', 'shake the audience', 'family/gospel', 'romantic', 'communication', 'obscene', 'music', 'movement/places', 'light/visual perceptions', 'family/spiritual', 'like/girls', 'sadness', 'feelings', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'topic', 'age']]
        logger.info(f"TCC_CEDS_MUSIC DataFrame loaded with columns: {TCC_CEDS_MUSIC.columns.tolist()}")
    except FileNotFoundError:
        TCC_CEDS_MUSIC = pd.DataFrame(columns=['track_name', 'artist_name', 'release_date', 'genre', 'lyrics', 'len', 'dating', 'violence', 'world/life', 'night/time', 'shake the audience', 'family/gospel', 'romantic', 'communication', 'obscene', 'music', 'movement/places', 'light/visual perceptions', 'family/spiritual', 'like/girls', 'sadness', 'feelings', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy', 'topic', 'age'])
        logger.error("tcc_ceds_music.csv not found. TCC_CEDS_MUSIC dataset is empty.")

    return SONGS, TCC_CEDS_MUSIC

# Initialize datasets
SONGS, TCC_CEDS_MUSIC = load_datasets()

def fetch_spotify_metadata(track_name: str, artist_name: str) -> dict:
    """
    Fetches metadata for a given track and artist from Spotify.

    Parameters:
        track_name (str): The name of the track.
        artist_name (str): The name of the artist.

    Returns:
        dict: A dictionary containing track metadata.
    """
    query = f"track:{track_name} artist:{artist_name}"
    results = spotify.search(q=query, type='track', limit=1)
    tracks = results.get('tracks', {}).get('items', [])
    if not tracks:
        logger.warning(f"No Spotify results found for '{track_name}' by '{artist_name}'.")
        return {}

    track = tracks[0]
    metadata = {
        'track_name': track['name'],
        'artist_name': track['artists'][0]['name'],
        'album': track['album']['name'],
        'release_date': track['album']['release_date'],
        'genre': ', '.join(track['artists'][0]['genres']) if track['artists'][0]['genres'] else 'Unknown',
        'duration_ms': track['duration_ms'],
        'danceability': track['danceability'] if 'danceability' in track else 0,
        'energy': track['energy'] if 'energy' in track else 0,
        'valence': track['valence'] if 'valence' in track else 0,
        'acousticness': track['acousticness'] if 'acousticness' in track else 0,
        'instrumentalness': track['instrumentalness'] if 'instrumentalness' in track else 0,
        'tempo': track['tempo'] if 'tempo' in track else 0,
        # Add more attributes as needed
    }
    return metadata

def searchSong(name_song: str, artist_name: str) -> str:
    """
    Searches for a song on YouTube based on Spotify metadata and returns the URL.

    Parameters:
        name_song (str): The name of the song.
        artist_name (str): The name of the artist.

    Returns:
        str: YouTube URL of the song.
    """
    # Fetch Spotify metadata
    metadata = fetch_spotify_metadata(name_song, artist_name)
    if not metadata:
        # Fallback to using the original song name and artist name
        query = f"{name_song} {artist_name}"
    else:
        # Use Spotify metadata to form a better query
        query = f"{metadata['track_name']} {metadata['artist_name']}"

    videosSearch = VideosSearch(query, limit=1)
    result = videosSearch.result()
    if result['result']:
        link = result["result"][0]["link"]
        logger.debug(f"searchSong: Found YouTube URL {link} for '{name_song}' by '{artist_name}'.")
        return link
    else:
        logger.warning(f"No YouTube results found for query: {query}")
        return ""

def get_full_song_name(song_name: str, artist_name: str) -> Union[List[str], None]:
    """
    Returns the full song name and artist name by searching in the primary and alternate datasets.

    Parameters:
        song_name (str): Partial or full name of the song.
        artist_name (str): Name of the artist.

    Returns:
        list or None: [full_song_name, full_artist_name] or None if not found.
    """
    # Search in primary dataset
    song = SONGS.loc[
        (SONGS["track_name"].str.contains(song_name, case=False, na=False)) &
        (SONGS["artist_name"].str.contains(artist_name, case=False, na=False))
    ]

    if song.empty:
        # Search in alternate dataset
        song = TCC_CEDS_MUSIC.loc[
            (TCC_CEDS_MUSIC["track_name"].str.contains(song_name, case=False, na=False)) &
            (TCC_CEDS_MUSIC["artist_name"].str.contains(artist_name, case=False, na=False))
        ]

    if song.empty:
        logger.warning(f"Song '{song_name}' by '{artist_name}' not found in datasets.")
        return None

    # Return the first match
    full_song_name = song.iloc[0]['track_name']
    full_artist_name = song.iloc[0]['artist_name']
    return [full_song_name, full_artist_name]

def retrieve_song_attributes(songName: str, artistName: str) -> List[float]:
    """
    Retrieves attributes of a song using Spotify metadata.

    Parameters:
        songName (str): The name of the song.
        artistName (str): The name of the artist.

    Returns:
        list: A list of attributes for the song.
    """
    metadata = fetch_spotify_metadata(songName, artistName)
    if not metadata:
        return [0] * 22  # Adjust the length based on attributes
    # Extract relevant attributes in order
    attributes = [
        metadata.get('danceability', 0),
        metadata.get('energy', 0),
        metadata.get('valence', 0),
        metadata.get('acousticness', 0),
        metadata.get('instrumentalness', 0),
        metadata.get('tempo', 0),
        # Add more attributes as needed
    ]
    return attributes

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
            (all_songs_alt["artist_name"].str.lower() == artistName.lower())
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
