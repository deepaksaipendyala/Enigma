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
        if (self.current_index == len(self.queue) - 1):
            self.current_index = 0
        else:
            self.current_index += 1
        val = self.current_index
        return self.queue[val]

    """
    This function returns the previous song in the queue
    """

    def prev_song(self):
        self.current_index -= 1
        if (self.current_index < 0):
            self.current_index = len(self.queue) - 1
        val = self.current_index
        return self.queue[val]

    """
    This function moves a song within the queue
    """

    def move_song(self, song_name, idx):
        curr_idx = -1
        if int(idx) < 1 or int(idx) > len(self.queue) - 1:
            return -2
        for index, s in enumerate(self.queue):
            if s.upper() == song_name.upper():
                curr_idx = index
        if curr_idx != -1:
            element = self.queue.pop(curr_idx)  # Remove the element from the old index
            self.queue.insert(int(idx), element)  # Insert the element at the new index
            return int(idx)
        else:
            return -1

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
        element = self.queue.pop(self.current_index)
        shuffle(self.queue)
        self.queue.insert(self.current_index, element)

    def add_to_queue(self, song_name):
        self.queue.append(song_name)
    
    def remove_from_queue(self, song_name):
        for index, s in enumerate(self.queue):
            if s.upper() == song_name.upper():
                if index != self.current_index: 
                    return self.queue.pop(index)
                else:
                    self.queue.pop(index)
                    self.current_index -= 1
                    if (self.current_index < 0):
                        self.current_index = len(self.queue) - 1
                    return index
        return -1
