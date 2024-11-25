# cogs/helpers/songs_queue.py
"""
This file is responsible for maintaining the song queue
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
    Songs are stored as tuples: (track_name, artist_name).
    """

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._queue: List[Tuple[str, str]] = []
            self._index: int = 0
            self._initialized = True
            logger.info("Songs_Queue initialized with an empty queue.")

    @property
    def queue(self) -> List[Tuple[str, str]]:
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
                "No songs present in the queue. Please add songs using !play or !add."
            )
            logger.info("handle_empty_queue: Queue is empty.")
            return True
        return False

    def clear(self):
        """Clears the entire queue and resets the index."""
        self._queue.clear()
        self._index = 0
        logger.info("Queue cleared and index reset to 0.")
        logger.debug(f"clear: Current queue: {self._queue}")

    def get_song_at_index(self, idx: int) -> Union[Tuple[str, str], int]:
        """
        Retrieves the song at a specific index.

        Parameters:
            idx (int): Index of the song in the queue.

        Returns:
            Tuple[str, str]: (track_name, artist_name)
            int: -1 if index is invalid.
        """
        if idx < 0 or idx >= len(self.queue):
            logger.warning(f"get_song_at_index: Invalid index {idx}.")
            return -1
        song = self._queue[idx]
        logger.debug(f"get_song_at_index: Retrieved song {song} at index {idx}.")
        return song

    def current_song(self) -> Union[Tuple[str, str], int]:
        """Returns the current song without modifying the queue."""
        current = self.get_song_at_index(self._index)
        logger.debug(f"current_song: Current song is {current}.")
        return current

    def next_song(self) -> Union[Tuple[str, str], int]:
        """
        Advances to the next song in the queue.

        Returns:
            Tuple[str, str]: Next song tuple.
            int: -1 if queue is empty.
        """
        if not self._queue:
            logger.info("next_song: Queue is empty.")
            return -1
        self._index = (self._index + 1) % len(self._queue)
        logger.info(f"next_song: Moved to index {self._index}.")
        next_song = self.get_song_at_index(self._index)
        logger.debug(f"next_song: Next song is {next_song}.")
        return next_song

    def prev_song(self) -> Union[Tuple[str, str], int]:
        """
        Goes back to the previous song in the queue.

        Returns:
            Tuple[str, str]: Previous song tuple.
            int: -1 if queue is empty.
        """
        if not self._queue:
            logger.info("prev_song: Queue is empty.")
            return -1
        self._index = (self._index - 1) % len(self._queue)
        logger.info(f"prev_song: Moved to index {self._index}.")
        prev_song = self.get_song_at_index(self._index)
        logger.debug(f"prev_song: Previous song is {prev_song}.")
        return prev_song

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
        logger.info(f"move_song: Moved '{song_name}' to position {new_position}.")

        # Adjust current index if necessary
        if current_idx < self._index < new_position - 1:
            self._index -= 1
        elif new_position - 1 <= self._index < current_idx:
            self._index += 1
        elif self._index == current_idx:
            self._index = new_position - 1

        logger.debug(f"move_song: Current index is now {self._index}.")
        logger.debug(f"move_song: Current queue: {self._queue}")
        return self._index

    def get_len(self) -> int:
        """Returns the number of songs in the queue."""
        return len(self._queue)

    def return_queue(self) -> Tuple[List[Tuple[str, str]], int]:
        """
        Returns the entire queue and the current index.

        Returns:
            Tuple[List[Tuple[str, str]], int]: (queue, current_index)
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
        logger.info("shuffle_queue: Queue shuffled while keeping the current song in place.")
        logger.debug(f"shuffle_queue: Current queue: {self._queue}")

    def add_to_queue(self, songs: Union[Tuple[str, str], List[Tuple[str, str]]]):
        """
        Adds one or multiple songs to the queue.

        Parameters:
            songs (Tuple[str, str] or List[Tuple[str, str]]): Song(s) to add.
        """
        if isinstance(songs, list):
            for song in songs:
                if isinstance(song, tuple) and len(song) == 2:
                    self._queue.append(song)
                    logger.info(f"add_to_queue: Added '{song[0]}' by '{song[1]}' to the queue.")
                else:
                    self._queue.append((song, "Unknown"))
                    logger.warning(f"add_to_queue: Added '{song}' by 'Unknown' to the queue.")
        elif isinstance(songs, tuple) and len(songs) == 2:
            self._queue.append(songs)
            logger.info(f"add_to_queue: Added '{songs[0]}' by '{songs[1]}' to the queue.")
        else:
            self._queue.append((songs, "Unknown"))
            logger.warning(f"add_to_queue: Added '{songs}' by 'Unknown' to the queue.")

        logger.debug(f"add_to_queue: Current queue: {self._queue}")

    def remove_from_queue(self, song_name: str) -> Union[Tuple[str, str], int]:
        """
        Removes a song from the queue by name.

        Parameters:
            song_name (str): Name of the song to remove.

        Returns:
            Tuple[str, str]: Removed song.
            int: -1 if not found.
        """
        for index, song in enumerate(self._queue):
            if song[0].lower() == song_name.lower():
                removed_song = self._queue.pop(index)
                logger.info(f"remove_from_queue: Removed '{removed_song[0]}' by '{removed_song[1]}' from the queue.")
                # Adjust current index if necessary
                if index < self._index or self._index >= len(self._queue):
                    self._index = max(0, self._index - 1)
                logger.debug(f"remove_from_queue: Current queue: {self._queue}")
                return removed_song
        logger.warning(f"remove_from_queue: Song '{song_name}' not found in queue.")
        return -1
