from pathlib import Path
import threading
from typing import Union

from logger import Logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class SyncDogObserver():
    """
    SyncDogObserver is a class that monitors a specified directory for file
    system events using a provided handler. It allows changing the directory,
    starting, and stopping the observation process.
    Attributes:
        handler (FileSystemEventHandler): The handler that processes file system
            events.
        directory (Path | str): The directory to be monitored.
        _is_running (bool): A flag indicating whether the observer is currently
            running.
        _stop_event (threading.Event): An event used to signal the observer to
            stop.
    Methods:
        set_directory(new_directory: Union[Path, str]) -> None:
        run() -> None:
            Schedules the handler to monitor the specified directory
                recursively, starts the observer, and sets the running flag to
                True.
        stop() -> None:
            Sends a stop event to the observer.
        is_running() -> bool:
            Checks if the observer is currently running.
        __repr__() -> str:
            Returns a string representation of the SyncDogObserver instance.
        __str__() -> str:
            Returns a user-friendly string representation of the SyncDogObserver
                instance.
    """

    def __init__(
            self,
            directory: Union[Path | str, list] = None,
            file_handler: FileSystemEventHandler = None
    ) -> None:
        super().__init__()
        self.handler = file_handler
        self.directory = directory
        self._is_running = False
        self._stop_event = threading.Event()

    def run(self) -> None:
        """
        This method schedules the handler to monitor the specified directory
        recursively, starts the observer, and sets the running flag to True.
        It then enters a loop, waiting for a stop event to be set. Once the
        stop event is detected, it stops and joins the observer, and sets the
        running flag to False.
        """
        self.observer = Observer()
        if isinstance(self.directory, list):
            self.observer.schedule(
                self.handler, self.directory[0], recursive=True)
            self.observer.schedule(
                self.handler, self.directory[1], recursive=True)
        else:
            self.observer.schedule(
                self.handler, self.directory, recursive=True)
        self.observer.start()
        self._is_running = True
        logger.debug("\nWatcher Running in {}\n".format(self.directory))
        while not self._stop_event.is_set():
            self._stop_event.wait(1)

        self.observer.stop()
        self.observer.join()

        self._is_running = False

    def stop(self) -> None:
        """Sends stop event."""
        self._stop_event.set()

    def set_directory(self, new_directory: Union[Path, str, list]) -> None:
        """
        Sets the current working directory to the specified new directory.

        Args:
            new_directory (Union[Path, str]): The new directory to change to. It
                can be either a Path object or a string representing the path.
        Raises:
            RuntimeError: If the observer is currently running.
        """
        if self.is_running:
            raise RuntimeError(
                "Cannot change directory while observer is running."
            )
        self.directory = new_directory

    @property
    def is_running(self) -> bool:
        """
        Check if the observer is currently running.

        Returns:
            bool: True if the observer is running, False otherwise.
        """
        return self._is_running

    def __repr__(self) -> str:
        return f"SyncDogObserver(directory={self.directory!r}, " \
            f"handler={self.handler!r})"

    def __str__(self) -> str:
        if self.directory:
            return f"SyncDogObserver monitoring directory: {self.directory}"
        else:
            return "SyncDogObserver not monitoring any directory."
