import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
import scripts.eda_analysis

class TestEdaAnalysis(unittest.TestCase):

    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv):
        # Setup.
        mock_read_csv.return_value = pd.DataFrame({
            'track_name': ['Song1', 'Song2'],
            'artist_name': ['Artist1', 'Artist2'],
            'bpm': [100, 200]
        })
        
        songs_df = pd.read_csv('.\\data\\songs.csv')
        
        self.assertFalse(songs_df.empty)
        self.assertEqual(len(songs_df), 2)
        mock_read_csv.assert_called_with('.\\data\\songs.csv')

    def test_missing_values_identification(self):
        # Setup.
        data = pd.DataFrame({
            'track_name': ['Song1', None, 'Song3'],
            'artist_name': ['Artist1', 'Artist2', None]
        })
        
        missing_values_count = data.isnull().sum()
        
        self.assertEqual(missing_values_count['track_name'], 1)
        self.assertEqual(missing_values_count['artist_name'], 1)

    def test_duplicate_detection(self):
        # Setup.
        data = pd.DataFrame({
            'track_name': ['Song1', 'Song1', 'Song2'],
            'artist_name': ['Artist1', 'Artist1', 'Artist2']
        })
        
        duplicates_count = data.duplicated(subset=['track_name', 'artist_name']).sum()
        
        self.assertEqual(duplicates_count, 1)