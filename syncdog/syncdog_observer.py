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
    def __init__(
            self,
            directory: Path | str = None,
            file_handler: FileSystemEventHandler = None
    ) -> None:
        super().__init__()
        self.observer = Observer()
        self.handler = file_handler
        self.directory = directory
        self._is_running = False
        self._stop_event = threading.Event()

    def change_directory(self, new_directory: Union[Path, str]) -> None:
        """
        Changes the current working directory to the specified new directory.

        Args:
            new_directory (Union[Path, str]): The new directory to change to. It
                can be either a Path object or a string representing the path.
        Raises:
            RuntimeError: If the observer is currently running.

        Notes:
            If the observer is currently running, it will be stopped before
                changing the directory.
        """
        if self.is_running:
            raise RuntimeError(
                "Cannot change directory while observer is running."
            )
        self.directory = new_directory

    def run(self) -> None:
        """
        This method schedules the handler to monitor the specified directory
        recursively, starts the observer, and sets the running flag to True.
        It then enters a loop, waiting for a stop event to be set. Once the
        stop event is detected, it stops and joins the observer, and sets the
        running flag to False.
        """
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        self._is_running = True
        logger.debug("\nWatcher Running in {}/\n".format(self.directory))
        while not self._stop_event.is_set():
            self._stop_event.wait(1)

        self.observer.stop()
        self.observer.join()

        self._is_running = False

    def stop(self) -> None:
        """Sends stop event."""
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        """
        Check if the observer is currently running.

        Returns:
            bool: True if the observer is running, False otherwise.
        """
        return self._is_running
