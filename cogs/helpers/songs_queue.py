"""
This file is responsible for maintaining the song queue.
"""

from typing import Tuple, List, Union
from random import shuffle
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

class Singleton(type):
    """A metaclass that creates a Singleton base type when called."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Create a new instance of the class if it does not exist."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logger.info(f"Creating new instance of {cls.__name__}")
        return cls._instances[cls]

class Songs_Queue(metaclass=Singleton):
    """
    Singleton class responsible for maintaining the song queue.
    Songs are stored as tuples: (track_name, artist_name, source, url).
    """

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._queue: List[Tuple[str, str, str, Union[str, None]]] = []  # (track_name, artist_name, source, url)
            self._index: int = 0
            self._initialized = True
            logger.info("Songs_Queue initialized with an empty queue.")

    @property
    def queue(self) -> List[Tuple[str, str, str, Union[str, None]]]:
        """Returns the current song queue."""
        return self._queue

    @property
    def index(self) -> int:
        """Returns the current index in the queue."""
        return self._index

    async def handle_empty_queue(self, ctx) -> bool:
        """
        Helper function to handle empty song queue.

        Parameters:
            ctx: The context from Discord.

        Returns:
            bool: True if the queue is empty, False otherwise.
        """
        if self.get_len() == 0:
            await ctx.send(
                "❌ No songs present in the queue. Please add songs using !play or !add."
            )
            logger.info("handle_empty_queue: Queue is empty.")
            return True
        return False

    def clear(self):
        """Clears the entire queue and resets the index."""
        self._queue.clear()
        self._index = 0
        logger.info("Queue cleared and index reset to 0.")

    def get_song_at_index(self, idx: int) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """
        Retrieves the song at a specific index.

        Parameters:
            idx (int): Index of the song in the queue.

        Returns:
            Tuple[str, str, str, Union[str, None]]: (track_name, artist_name, source, url)
            int: -1 if index is invalid.
        """
        if idx < 0 or idx >= len(self.queue):
            logger.warning(f"get_song_at_index: Invalid index {idx}.")
            return -1
        return self._queue[idx]

    def current_song(self) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """Returns the current song without modifying the queue."""
        return self.get_song_at_index(self._index)

    def next_song(self) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """
        Advances to the next song in the queue.

        Returns:
            Tuple[str, str, str, Union[str, None]]: Next song tuple.
            int: -1 if queue is empty.
        """
        if not self._queue:
            logger.info("next_song: Queue is empty.")
            return -1
        self._index = (self._index + 1) % len(self._queue)
        return self.get_song_at_index(self._index)

    def prev_song(self) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """
        Goes back to the previous song in the queue.

        Returns:
            Tuple[str, str, str, Union[str, None]]: Previous song tuple.
            int: -1 if queue is empty.
        """
        if not self._queue:
            logger.info("prev_song: Queue is empty.")
            return -1
        self._index = (self._index - 1) % len(self._queue)
        return self.get_song_at_index(self._index)

    def remove_from_queue_by_index(self, idx: int) -> Union[Tuple[str, str, str], int]:
        """
        Removes a song from the queue by its index.
        """
        if idx < 0 or idx >= len(self._queue):
            logger.warning(f"remove_from_queue_by_index: Invalid index {idx}.")
            return -1
        song = self._queue.pop(idx)
        logger.info(f"remove_from_queue_by_index: Removed '{song[0]}' by '{song[1]}' from index {idx}.")
        # Adjust current index as needed
        if idx < self._index:
            self._index -= 1
        elif idx == self._index:
            if self._queue:
                self._index = self._index % len(self._queue)
            else:
                self._index = 0
        logger.debug(f"remove_from_queue_by_index: Current index is now {self._index}.")
        logger.debug(f"remove_from_queue_by_index: Current queue: {self._queue}")
        return song

    def move_song_by_index(self, current_idx: int, new_idx: int) -> int:
        """
        Moves a song from current_idx to new_idx in the queue.
        Returns the new index or -1 if invalid.
        """
        if new_idx < 0 or new_idx >= len(self._queue):
            logger.warning(f"move_song_by_index: Invalid new index {new_idx}.")
            return -1
        if current_idx < 0 or current_idx >= len(self._queue):
            logger.warning(f"move_song_by_index: Invalid current index {current_idx}.")
            return -1
        song = self._queue.pop(current_idx)
        self._queue.insert(new_idx, song)
        logger.info(f"move_song_by_index: Moved '{song[0]}' by '{song[1]}' from index {current_idx} to {new_idx}.")
        # Adjust current index as needed
        if current_idx < self._index <= new_idx:
            self._index -= 1
        elif new_idx <= self._index < current_idx:
            self._index += 1
        elif self._index == current_idx:
            self._index = new_idx
        logger.debug(f"move_song_by_index: Current index is now {self._index}.")
        logger.debug(f"move_song_by_index: Current queue: {self._queue}")
        return self._index

    def move_song(self, song_name: str, new_position: int) -> int:
        """
        Moves a song to a new position in the queue.

        Parameters:
            song_name (str): Name of the song to move.
            new_position (int): New index position (1-based).

        Returns:
            int: New index if successful, -1 if song not found, -2 if position invalid.
        """
        if new_position < 1 or new_position > len(self._queue):
            logger.warning(f"move_song: Invalid new_position {new_position}.")
            return -2

        # Find the song index
        current_idx = next((i for i, song in enumerate(self._queue) if song[0].lower() == song_name.lower()), -1)
        if current_idx == -1:
            logger.warning(f"move_song: Song '{song_name}' not found in queue.")
            return -1

        # Remove and insert the song
        song = self._queue.pop(current_idx)
        self._queue.insert(new_position - 1, song)

        # Adjust current index if necessary
        if current_idx < self._index < new_position - 1:
            self._index -= 1
        elif new_position - 1 <= self._index < current_idx:
            self._index += 1
        elif self._index == current_idx:
            self._index = new_position - 1

        return self._index

    def get_len(self) -> int:
        """Returns the number of songs in the queue."""
        return len(self._queue)

    def return_queue(self) -> Tuple[List[Tuple[str, str, str, Union[str, None]]], int]:
        """
        Returns the entire queue and the current index.

        Returns:
            Tuple[List[Tuple[str, str, str, Union[str, None]]], int]: (queue, current_index)
        """
        return (self._queue.copy(), self._index)

    def shuffle_queue(self):
        """Shuffles the queue while keeping the current song in place."""
        if not self._queue:
            logger.info("shuffle_queue: Queue is empty. Nothing to shuffle.")
            return
        current_song = self._queue.pop(self._index)
        shuffle(self._queue)
        self._queue.insert(self._index, current_song)

    def add_to_queue(self, songs: Union[Tuple[str, str, str, Union[str, None]], List[Tuple[str, str, str, Union[str, None]]]]):
        """
        Adds one or multiple songs to the queue.

        Parameters:
            songs (Tuple[str, str, str, Union[str, None]] or List[Tuple[str, str, str, Union[str, None]]]): Song(s) to add.
        """
        if isinstance(songs, list):
            self._queue.extend(songs)
        else:
            self._queue.append(songs)

    def remove_from_queue(self, song_name: str) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """
        Removes a song from the queue by name.

        Parameters:
            song_name (str): Name of the song to remove.

        Returns:
            Tuple[str, str, str, Union[str, None]]: Removed song.
            int: -1 if not found.
        """
        for index, song in enumerate(self._queue):
            if song[0].lower() == song_name.lower():
                removed_song = self._queue.pop(index)
                # Adjust current index if necessary
                if index < self._index or self._index >= len(self._queue):
                    self._index = max(0, self._index - 1)
                return removed_song
        return -1

    def remove_at_index(self, index: int) -> Union[Tuple[str, str, str, Union[str, None]], int]:
        """
        Removes a song from the queue by its index.

        Parameters:
            index (int): The index of the song to remove.

        Returns:
            Tuple[str, str, str, Union[str, None]]: Removed song.
            int: -1 if index is invalid.
        """
        if 0 <= index < len(self._queue):
            removed_song = self._queue.pop(index)
            # Adjust current index if necessary
            if index <= self._index:
                self._index = max(0, self._index - 1)
            return removed_song
        return -1
