import unittest
from src.recommend_enhanced import recommend_enhanced


class EnhancedRecommendTest(unittest.TestCase):
    """
    This class is responsible for testing the enhanced recommendation system
    """

    def test_recommend_enhanced_one_song(self):
        """
        This function tests the enhanced recommendation system
        """
        input_songs = [("the carioca", "les paul")]
        songs = recommend_enhanced(input_songs)
        print(songs)
        self.assertTrue(len(songs) == 10)

    def test_recommend_enhanced_two_songs(self):
        """
        This function tests the enhanced recommendation system
        """

        input_songs = [("the carioca", "les paul"), ("cry", "johnnie ray")]
        songs = recommend_enhanced(input_songs)
        print(songs)
        self.assertTrue(len(songs) == 10)

    def test_random_recommendations(self):
        """
        This function tests the enhanced recommendation system
        """

        input_songs = [("the carioca", "les paul")]
        songs1 = recommend_enhanced(input_songs)
        print(songs1)
        self.assertTrue(len(songs1) == 10)
        
        songs2 = recommend_enhanced(input_songs)
        print(songs2)
        self.assertTrue(len(songs2) == 10)

        self.assertNotEqual(songs1, songs2)