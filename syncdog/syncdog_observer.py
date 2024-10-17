from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from pathlib import Path
from logger import Logger


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class SyncDogObserver:
    def __init__(
            self,
            directory: Path | str,
            file_handler: FileSystemEventHandler
    ) -> None:
        self.observer = Observer()
        self.handler = file_handler
        self.directory = directory
        self._is_running = False

    def change_directory(self, new_directory: Path | str) -> None:
        """
        Changes the current working directory to the specified new directory.

        Args:
            new_directory (Path | str): The new directory to change to. It can
                be either a Path object or a string representing the path.

        Returns:
            None

        Logs:
            DEBUG: Logs the directory change from the current directory to the
                new directory.

        Notes:
            If the observer is currently running, it will be stopped before
                changing the directory.
        """
        logger.debug(
            f"Changing directory from {self.directory} to {new_directory}"
        )
        if self.is_running():
            self.stop()
        self.directory = new_directory

    def run(self) -> None:
        """
        Starts the observer to monitor the directory for changes.

        Schedules the handler, starts the observer, and sets the running flag.
        Handles KeyboardInterrupt to stop the observer gracefully.

        Raises:
            KeyboardInterrupt: If interrupted by a keyboard signal.
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
