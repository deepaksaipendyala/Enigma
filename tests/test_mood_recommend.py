import pandas as pd
import unittest
from unittest.mock import patch, MagicMock
from cogs.songs_cog import get_recommended_songs_based_on_mood


class TestSongsCog(unittest.TestCase):

    @patch('pandas.read_csv')
    def test_get_recommended_songs_based_on_mood_happy(self, mock_read_csv):
        # Setup mock data.
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5'],
            'artist_name': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
            'valence': [0.8, 0.9, 0.6, 0.85, 0.75],
            'energy': [0.7, 0.8, 0.65, 0.9, 0.85]
        })
        mock_read_csv.return_value = mock_data

        # Define filter for happy mood.
        filters = {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)}

        result = get_recommended_songs_based_on_mood(filters)

        self.assertEqual(result, ['Song1', 'Song2', 'Song4', 'Song5'])

    @patch('pandas.read_csv')
    def test_get_recommended_songs_based_on_mood_sad(self, mock_read_csv):
        # Setup mock data.
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5'],
            'artist_name': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
            'sadness': [0.8, 0.4, 0.6, 0.85, 0.3],
            'valence': [0.2, 0.4, 0.3, 0.25, 0.1],
            'energy': [0.3, 0.45, 0.5, 0.2, 0.15]
        })
        mock_read_csv.return_value = mock_data

        # Define filter for sad mood.
        filters = {'sadness': (0.5, 1), 'valence': (
            0.0, 0.3), 'energy': (0.2, 0.5)}

        result = get_recommended_songs_based_on_mood(filters)

        self.assertEqual(result, ['Song1', 'Song3', 'Song4'])
