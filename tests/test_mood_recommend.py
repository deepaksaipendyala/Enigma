import pandas as pd
import unittest
from unittest.mock import patch
from cogs.songs_cog import get_recommended_songs_based_on_mood


class TestSongsCog(unittest.TestCase):
    @patch('pandas.read_csv')
    def test_get_recommended_songs_based_on_mood_happy(self, mock_read_csv):
        # Mock dataset with required columns
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5'],
            'artist': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
            'valence': [0.8, 0.9, 0.6, 0.85, 0.75],
            'energy': [0.7, 0.8, 0.65, 0.9, 0.85]
        })
        mock_read_csv.return_value = mock_data

        # Define filters for happy mood
        filters = {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)}

        # Call the function
        result = get_recommended_songs_based_on_mood(filters)

        # Validate results
        expected = [
            ('Song1', 'Artist1'),
            ('Song2', 'Artist2'),
            ('Song4', 'Artist4'),
            ('Song5', 'Artist5')
        ]
        self.assertEqual(result, expected)

    @patch('pandas.read_csv')
    def test_get_recommended_songs_based_on_mood_sad(self, mock_read_csv):
        # Mock dataset with required columns
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2', 'Song3', 'Song4', 'Song5'],
            'artist': ['Artist1', 'Artist2', 'Artist3', 'Artist4', 'Artist5'],
            'sadness': [0.8, 0.4, 0.6, 0.85, 0.3],
            'valence': [0.2, 0.4, 0.3, 0.25, 0.1],
            'energy': [0.3, 0.45, 0.5, 0.2, 0.15]
        })
        mock_read_csv.return_value = mock_data

        # Define filters for sad mood
        filters = {'sadness': (0.5, 1), 'valence': (0.0, 0.3), 'energy': (0.2, 0.5)}

        # Call the function
        result = get_recommended_songs_based_on_mood(filters)

        # Validate results
        expected = [
            ('Song1', 'Artist1'),
            ('Song3', 'Artist3'),
            ('Song4', 'Artist4')
        ]
        self.assertEqual(result, expected)

    @patch('pandas.read_csv')
    def test_get_recommended_songs_based_on_empty_dataset(self, mock_read_csv):
        # Mock empty dataset
        mock_read_csv.return_value = pd.DataFrame(columns=['track_name', 'artist', 'valence', 'energy'])

        # Define filters
        filters = {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)}

        # Call the function
        result = get_recommended_songs_based_on_mood(filters)

        # Validate results
        self.assertEqual(result, [])

    @patch('pandas.read_csv')
    def test_get_recommended_songs_with_missing_columns(self, mock_read_csv):
        # Mock dataset missing a required column
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2'],
            'valence': [0.8, 0.9],
            'energy': [0.7, 0.8]
        })
        mock_read_csv.return_value = mock_data

        # Define filters
        filters = {'valence': (0.7, 1.0), 'energy': (0.5, 1.0)}

        # Call the function
        with self.assertLogs('cogs.helpers.get_all', level='ERROR') as log:
            result = get_recommended_songs_based_on_mood(filters)
            self.assertEqual(result, [])
            self.assertIn("Dataset is missing required columns", log.output[0])

    @patch('pandas.read_csv')
    def test_get_recommended_songs_invalid_filter(self, mock_read_csv):
        # Mock dataset
        mock_data = pd.DataFrame({
            'track_name': ['Song1', 'Song2', 'Song3'],
            'artist': ['Artist1', 'Artist2', 'Artist3'],
            'valence': [0.8, 0.9, 0.6],
            'energy': [0.7, 0.8, 0.65]
        })
        mock_read_csv.return_value = mock_data

        # Define invalid filters
        filters = {'invalid_column': (0.7, 1.0)}

        # Call the function
        result = get_recommended_songs_based_on_mood(filters)

        # Validate that all rows are returned as no filtering occurs with invalid filters
        expected = [
            ('Song1', 'Artist1'),
            ('Song2', 'Artist2'),
            ('Song3', 'Artist3')
        ]
        self.assertEqual(result, expected)

