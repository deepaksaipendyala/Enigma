import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Spotify authentication
client_credentials_manager = SpotifyClientCredentials(client_id='87f0fd217127470e8d55171d92e5cd33', client_secret='6094043b04f14d4a98600f76be162838')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def fetch_spotify_popularity(song_name, artist_name):
    """
    Fetch the popularity of a song using the Spotify API.
    """
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track['popularity']  # Popularity score (0-100).
    return None

# Load dataset.
songs_df = pd.read_csv('.\\data\\tcc_ceds_music.csv')

# Create a new column to store the popularity.
songs_df['popularity'] = None

# Iterate over each song and fetch popularity
for idx, row in songs_df.iterrows():
    song_name = row['track_name']
    artist_name = row['artist_name']
    popularity = fetch_spotify_popularity(song_name, artist_name)
    # print(f'Music: {row["track_name"]} Artist: {row["artist_name"]} {popularity}')
    songs_df.at[idx, 'popularity'] = popularity

    # To avoid hitting rate limits, sleep for a bit between requests
    time.sleep(1)

# Save the updated dataset with popularity
songs_df.to_csv('tcc_ceds_music_with_popularity.csv', index=False)

print("Popularity data has been added to the dataset.")