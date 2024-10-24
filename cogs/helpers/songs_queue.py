"""
This file is responsible for maintaining the song queue
"""
from random import shuffle

# Make a singleton class for the song queue
class Singleton(type):
    """A metaclass that creates a Singleton base type when called."""
    _instances= {}

    def __call__(cls, *args, **kwargs):
        """Create a new instance of the class if it does not exist."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Songs_Queue(metaclass=Singleton):
    """
    This class is responsible for maintaining the song queue. There will only be one instance of this class
    """

    def __init__(self):
        """Create a new instance of the Songs_Queue class, with an initially empty queue."""
        self._queue = []
        self.current_index = 0


    @property
    def queue(self):
        """Return the current queue."""
        return self._queue


    def clear(self):
        """Clear the current queue."""
        self._queue.clear()
        self.current_index = 0


    def next_song(self):
        """
        This function returns the next song in the queue
        """
        
        print(self.queue)
        if (self.current_index == len(self.queue) - 1):
            self.current_index = 0
        else:
            self.current_index += 1
        val = self.current_index
        return self.queue[val]


    def prev_song(self):
        """
        This function returns the previous song in the queue
        """

        self.current_index -= 1
        if (self.current_index < 0):
            self.current_index = len(self.queue) - 1
        val = self.current_index
        return self.queue[val]


    def move_song(self, song_name, idx):
        """
        This function moves a song within the queue
        """

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


    def get_len(self):
        """
        This function returns the length of the song queue
        """

        return len(self.queue)


    def return_queue(self):
        """
        This function returns song queue and the current index of the song that is playing
        """
        
        return (self.queue, self.current_index)


    def shuffle_queue(self):
        """
        This function shuffles the song queue
        """
        element = self.queue.pop(self.current_index)
        shuffle(self.queue)
        self.queue.insert(self.current_index, element)


    def add_to_queue(self, song_name: str|list[str]):
        """
        This function adds a song to the queue

        Parameters:
            song_name(str | list[str]): The name of the song to be added to the queue, or a list of song names to be added to the queue
        """

        if isinstance(song_name, list):
            self.queue.extend(song_name)
        else:
            self.queue.append(song_name)


    def remove_from_queue(self, song_name):
        """
        This function removes a song from the queue

        Parameters:
            song_name(str): The name of the song to be removed from the queue

        Returns:
            int: The index of the song that was removed from the queue, or -1 if the song was not found in the queue
        """

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
