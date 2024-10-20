from src.utils import retrieve_song_attributes, cosine_similarity
from src.get_all import get_all_songs

def recommend_enhanced(input_songs: list) -> list:
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
            input_song_attributes[(song_name, artist_name)] = song_attributes
    
    # Get the song attributes for all the songs
    all_song_attributes = {}
    for index, row in all_songs.iterrows():
        song_name = row["track_name"]
        artist_name = row["artist_name"]
        song_attributes = retrieve_song_attributes(song_name, artist_name)
        if song_attributes is not None:
            all_song_attributes[(song_name, artist_name)] = song_attributes

    # Calculate the cosine similarity between the input songs and all the songs. The final similarity score 
    # for each song will be the average of all the cosine similarities between the input songs and the song

    # Create a list to store the cosine similarity for each song. Will be stored in the format ((song_name, artist_name), similarity_score)
    similarity_scores = []

    for song_name, artist_name in all_song_attributes.keys():
        similarity_score = 0
        for input_song_name, input_artist_name in input_song_attributes.keys():
            input_song_attributes = input_song_attributes[(input_song_name, input_artist_name)]
            all_song_attributes = all_song_attributes[(song_name, artist_name)]
            cosine_similarity = cosine_similarity(input_song_attributes, all_song_attributes)
            similarity_score += cosine_similarity
        
        similarity_score /= len(input_song_attributes)
        similarity_scores.append([(song_name, artist_name), similarity_score])

    # Sort the similarity scores in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # return the song name and artist name for the top 10 songs
    recommended_songs = [x[0] for x in similarity_scores[:10]]
    return recommended_songs
