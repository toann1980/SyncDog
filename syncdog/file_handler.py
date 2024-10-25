from pathlib import Path
import shutil
from typing import Union

from logger import Logger

from syncdog.base_handler import BaseHandler
from syncdog.constants import FileSystemEvents


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class FileHandler(BaseHandler):
    def __init__(
            self,
            source: Union[str, Path] = None,
            destination: Union[str, Path] = None,
            debounce_interval: float = 0.5
    ) -> None:
        """
        Initializes the FileHandler with source, destination, and debounce
            interval.

        Args:
            source (Union[str, Path], optional): The source directory to
                monitor. Defaults to None.
            destination (Union[str, Path], optional): The destination directory.
                Defaults to None.
            debounce_interval (float, optional): The interval in seconds to
                debounce file system events. Defaults to 0.5.
        """
        super().__init__()
        self.source = None
        if source:
            self.set_source(source)
        self.destination = None
        self.patch_path: Path = None
        if destination:
            self.set_destination(destination)

        self.debounce_interval = debounce_interval

    def on_any_event(self, event: FileSystemEvents) -> None:
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.
        """
        if self.source is None or self.destination is None:
            return

        source_path = Path(event.src_path)
        if '.syncdog' in source_path.parts:
            return

        match event.event_type:
            case FileSystemEvents.CREATED.value:
                if event.is_directory:
                    self.create_directory(
                        self.source, source_path, self.destination)
                else:
                    self.track_work_file(
                        event.event_type, self.source, source_path,
                        self.destination, self.patch_path)
            case FileSystemEvents.DELETED.value:
                self.delete(self.source, source_path, self.destination)
            case FileSystemEvents.MOVED.value:
                self.rename(event, self.source, self.destination)
            case FileSystemEvents.MODIFIED.value:
                if self.working_files.get(source_path):
                    return
                self.track_work_file(
                    event.event_type, self.source, source_path,
                    self.destination, self.patch_path)

    def cleanup(self) -> None:
        """
        Cleans up the patch path by removing it if it exists.
        """
        if self.patch_path and self.patch_path.exists():
            shutil.rmtree(self.patch_path, ignore_errors=True)
            self.patch_path = None

    def set_destination(self, dest: Union[str, Path]) -> None:
        """
        Changes the destination directory to a new directory.

        Args:
            dest (Union[str, Path]): The new destination directory.
        """
        if self.patch_path and self.patch_path.exists():
            self.patch_path.rmdir()
        self.destination = Path(dest)
        self.patch_path = self.destination / '.syncdog'
        self.patch_path.mkdir(exist_ok=True)

    def set_source(self, source: Union[str, Path]) -> None:
        """
        Changes the source directory to a new directory.

        Args:
            source (Union[str, Path]): The new source directory to monitor.
        """
        self.source = Path(source)

    def __repr__(self):
        """
        Returns a string representation of the FileHandler instance.

        Returns:
            str: String representation of the FileHandler instance.
        """
        return f'{self.__class__.__name__}(source={self.source}, {self.dest})'

    def __str__(self):
        """
        Returns a human-readable string representation of the FileHandler
        instance.

        Returns:
            str: Human-readable string representation of the FileHandler
                instance.
        """
        return f'{self.__class__.__name__}: Source={self.source}, ' \
            f'Destination={self.dest}'
