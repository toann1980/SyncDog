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
        logger.debug(
            f"Changing directory from {self.directory} to {new_directory}"
        )
        if self.is_running():
            self.stop()
        self.directory = new_directory

    def run(self) -> None:
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
        self.observer.stop()
        self.observer.join()
        self._is_running = False

    def is_running(self) -> bool:
        return self._is_running
