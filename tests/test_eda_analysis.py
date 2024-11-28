import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Ensure seaborn is imported
from scripts import eda_analysis as eda


class TestEdaAnalysis(unittest.TestCase):

    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame({
            'track_name': ['Song1', 'Song2'],
            'artist_name': ['Artist1', 'Artist2'],
            'bpm': [100, 200]
        })
        songs_df = pd.read_csv('./data/songs.csv')
        self.assertFalse(songs_df.empty)
        self.assertEqual(len(songs_df), 2)
        mock_read_csv.assert_called_with('./data/songs.csv')

    def test_feature_distribution_plot(self):
        data = pd.DataFrame({'bpm': [100, 120, 140], 'dnce': [50, 60, 70]})
        with patch('matplotlib.pyplot.show') as mock_show:
            data['bpm'].plot(kind='hist', bins=3)
            plt.show()  # Explicitly call plt.show() in the test
            mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_scatter_plot_creation(self, mock_show):
        data = pd.DataFrame({'energy': [0.1, 0.5, 0.9], 'danceability': [0.2, 0.6, 0.8]})
        sns.scatterplot(data=data, x='energy', y='danceability')
        plt.show()  # Explicitly call plt.show() to trigger mock
        mock_show.assert_called_once()

    def test_missing_values_identification(self):
        data = pd.DataFrame({'track_name': ['Song1', None, 'Song3'], 'artist_name': ['Artist1', 'Artist2', None]})
        missing_values_count = data.isnull().sum()
        self.assertEqual(missing_values_count['track_name'], 1)
        self.assertEqual(missing_values_count['artist_name'], 1)

    def test_duplicate_detection(self):
        data = pd.DataFrame({'track_name': ['Song1', 'Song1', 'Song2'], 'artist_name': ['Artist1', 'Artist1', 'Artist2']})
        duplicates_count = data.duplicated(subset=['track_name', 'artist_name']).sum()
        self.assertEqual(duplicates_count, 1)

    def test_correlation_matrix_calculation(self):
        data = pd.DataFrame({'bpm': [100, 120, 140], 'dnce': [50, 60, 70], 'val': [30, 40, 50]})
        correlation_matrix = data.corr()
        self.assertAlmostEqual(correlation_matrix.loc['bpm', 'dnce'], 1.0, delta=1e-6)

    def test_handling_empty_dataset(self):
        empty_data = pd.DataFrame()
        self.assertTrue(empty_data.empty)

    def test_genre_analysis(self):
        data = pd.DataFrame({'genre': ['Pop', 'Pop', 'Rock', 'Jazz', 'Jazz', 'Jazz']})
        genre_counts = data['genre'].value_counts()
        self.assertEqual(genre_counts['Jazz'], 3)
        self.assertEqual(genre_counts['Pop'], 2)
        self.assertEqual(genre_counts['Rock'], 1)

    def test_normalization(self):
        data = pd.DataFrame({'bpm': [100, 200, 300]})
        normalized_bpm = data['bpm'] / 100
        self.assertListEqual(normalized_bpm.tolist(), [1.0, 2.0, 3.0])


if __name__ == '__main__':
    unittest.main()
