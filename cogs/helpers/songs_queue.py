"""
This file is responsible for maintaining the song queue
"""
from random import shuffle


class Songs_Queue():
    """
    This class is responsible for maintaining the song queue
    """

    def __init__(self, song_names):
        self.queue = song_names
        self.index = 0
        self.current_index = 0

    """
    This function returns the next song in the queue
    """

    def next_song(self):
        print(self.queue)
        if (self.index == len(self.queue)):
            self.index = 0
        val = self.index
        self.current_index = val
        self.index += 1
        return self.queue[val]

    """
    This function returns the previous song in the queue
    """

    def prev_song(self):
        self.index -= 1
        if (self.index <= 0):
            self.index = len(self.queue) - 1
        val = self.index
        self.current_index = val
        return self.queue[val]

    """
    This function returns the length of the song queue
    """

    def get_len(self):
        return len(self.queue)

    """
    This function returns song queue and the current index of the song that is playing
    """

    def return_queue(self):
        return (self.queue, self.current_index)

    def shuffle_queue(self):
        shuffle(self.queue)

    def add_to_queue(self, song_name):
        self.queue.append(song_name)