from cogs.helpers.recommend_enhanced import recommend_enhanced


def test_recommend_enhanced_one_song():
    """
    This function tests the enhanced recommendation system
    """
    input_songs = [("the carioca", "les paul")]
    songs = recommend_enhanced(input_songs)
    print(songs)
    assert len(songs) == 10


def test_recommend_enhanced_two_songs():
    """
    This function tests the enhanced recommendation system
    """

    input_songs = [("the carioca", "les paul"), ("cry", "johnnie ray")]
    songs = recommend_enhanced(input_songs)
    print(songs)
    assert len(songs) == 10


def test_random_recommendations():
    """
    This function tests the enhanced recommendation system
    """

    input_songs = [("the carioca", "les paul")]
    songs1 = recommend_enhanced(input_songs)
    print(songs1)
    assert len(songs1) == 10

    songs2 = recommend_enhanced(input_songs)
    print(songs2)
    assert len(songs2) == 10

    assert songs1 != songs2
