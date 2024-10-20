import unittest
import warnings
import sys
from src import utils

sys.path.append("../")
warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):

    # For testing the searchSong() method. Given a song name as input, should return the youtube link.
    def test_searchSong(self):
        song_name = "Watermelon Sugar"
        actual_link = utils.searchSong(song_name)
        expected_link = "https://www.youtube.com/watch?v=E07s5ZYygMg"
        self.assertTrue(actual_link == expected_link)


# For testing the random_25() method. Checking if the list returned is of length 25.

    def test_random_25(self):
        random_songs = utils.random_25()
        self.assertTrue(len(random_songs) == 25)




class CosSimTests(unittest.TestCase):

    def test_retrieve_song_attributes(self):
        song_name = "i believe"
        artist_name = "frankie laine"
        actual_song_attributes = utils.retrieve_song_attributes(song_name, artist_name)
        expected_song_attributes = [0.0355371338259024,0.09677674227829695,0.44343517381864045,0.0012836971138939872,0.0012836970540271917,0.02700747737752981,0.0012836971498796242,0.0012836971222831008,0.0012836971144120706,0.11803384116823598,0.001283697092589732,0.2126810671851602,0.05112419901776462,0.0012836970563617238,0.0012836971300268928,0.0012836971751683166,0.33174482833315283,0.64753993282568,0.9548192317462166,1.5283400809716598e-06,0.3250206100577081,0.2632402533492537]

        print(len(actual_song_attributes))

        self.assertTrue(len(actual_song_attributes) == len(expected_song_attributes))

        for i in range(len(actual_song_attributes)):
            expected_attr = round(expected_song_attributes[i], 10)
            actual_attr = round(actual_song_attributes[i], 10)
            self.assertEqual(expected_attr, actual_attr)

    # For testing the cosine_similarity() method. Given two song names, should return the cosine similarity between them.
    def test_cosine_similarity(self):
        song_name1 = "cry"
        artist_name1 = "johnnie ray"
        song_name2 = "the carioca"
        artist_name2 = "les paul"
        actual_cosine_similarity = utils.cosine_similarity(song_name1, artist_name1, song_name2, artist_name2)

        expected_cosine_similarity = 0.75044
        
        self.assertEqual(round(expected_cosine_similarity, 2), round(actual_cosine_similarity, 2))

    def test_not_found_song(self):
        song_name = "song"
        artist_name = "artist"
        actual_song_attributes = utils.retrieve_song_attributes(song_name, artist_name)
        
        expected_song_attributes = [0]*22

        self.assertEquals(actual_song_attributes, expected_song_attributes)

    def test_retrieve_attributes_alternate(self):

        song_name = "Hey, Soul Sister"
        artist_name = "Train"
        expected_song_attributes = [97,89,67,8,80,217,19,4,83]

        actual_song_attributes = utils.retrieve_attributes_alternate(song_name, artist_name)

        self.assertEquals(actual_song_attributes, expected_song_attributes)

    def test_one_not_found_song(self):
        song_name1 = "song"
        artist_name1 = "artist"
        song_name2 = "the carioca"
        artist_name2 = "les paul"
        actual_cosine_similarity = utils.cosine_similarity(song_name1, artist_name1, song_name2, artist_name2)

        self.assertEqual(actual_cosine_similarity, 0)

    def test_both_not_found_song(self):
        song_name1 = "song"
        artist_name1 = "artist"
        song_name2 = "song"
        artist_name2 = "artist"
        actual_cosine_similarity = utils.cosine_similarity(song_name1, artist_name1, song_name2, artist_name2)

        self.assertEqual(actual_cosine_similarity, 0)

    def test_both_found_alternate(self):
        song_name1 = "Hey, Soul Sister"
        artist_name1 = "Train"
        song_name2 = "Baby"
        artist_name2 = "Justin Bieber"
        actual_cosine_similarity = utils.cosine_similarity(song_name1, artist_name1, song_name2, artist_name2)

        expected_cosine_similarity = 0.9886360242
        self.assertEqual(round(actual_cosine_similarity, 4), round(expected_cosine_similarity, 4))

    def test_orthagonal_vectors(self):
        song_name1 = "TestSong1"
        artist_name1 = "TestArtist1"
        song_name2 = "TestSong2"
        artist_name2 = "TestArtist2"

        song1 = utils.retrieve_attributes_alternate(song_name1, artist_name1)
        song2 = utils.retrieve_attributes_alternate(song_name2, artist_name2)

        expected_song1 = [1,0,1,0,1,0,1,0,1]
        expected_song2 = [0,1,0,1,0,1,0,1,0]

        self.assertEqual(song1, expected_song1)
        self.assertEqual(song2, expected_song2)

        actual_cosine_similarity = utils.cosine_similarity(song_name1, artist_name1, song_name2, artist_name2)

        self.assertEqual(actual_cosine_similarity, 0)

    def test_get_full_song_name(self):
        song_name = "Hey, Soul"
        artist_name = "Train"
        full_song_name = utils.get_full_song_name(song_name, artist_name)
        expected_song_name = "Hey, Soul Sister"
        expected_artist_name = "Train"

        self.assertEqual(full_song_name[0], expected_song_name)
        self.assertEqual(full_song_name[1], expected_artist_name)