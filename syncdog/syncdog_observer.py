from pathlib import Path
from typing import Union

from logger import Logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from PySide6.QtCore import QThread

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class SyncDogObserver(QThread):
    def __init__(
            self,
            directory: Path | str,
            file_handler: FileSystemEventHandler
    ) -> None:
        super().__init__()
        self.observer = Observer()
        self.handler = file_handler
        self.directory = directory
        self._is_running = False

    def run(self) -> None:
        """
        Starts the observer to monitor the directory for changes.

        Schedules the handler, starts the observer, and sets the running flag.
        Handles KeyboardInterrupt to stop the observer gracefully.
        """
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        self._is_running = True
        logger.debug("\nWatcher Running in {}/\n".format(self.directory))
        try:
            self.observer.join()
        except KeyboardInterrupt:
            self.observer.stop()
            self.observer.join()

    def stop(self) -> None:
        """
        Stops the observer and waits for it to finish.

        This method stops the observer thread and waits for it to terminate,
        then sets the running flag to False.
        """
        if self.is_running():
            self.observer.stop()
            self.observer.join()
        self._is_running = False

    def is_running(self) -> bool:
        """
        Check if the observer is currently running.

        Returns:
            bool: True if the observer is running, False otherwise.
        """
        return self._is_running
