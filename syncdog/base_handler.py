from abc import ABC, abstractmethod
import contextlib
import os
from pathlib import Path
import shutil
import time
import threading
from typing import Union

from logger import Logger

import bsdiff4
from getfiles import get_files
from watchdog.events import FileSystemEventHandler
from syncdog.constants import FileSystemEvents

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")

# TODO: check for relative_to


class BaseHandler(FileSystemEventHandler, ABC):
    def __init__(
            self,
            debounce_interval: float = 0.50
    ) -> None:
        super().__init__()
        self.debounce_interval = debounce_interval
    
    @abstractmethod
    def on_any_event(self, event: FileSystemEvents):
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        pass
    
    # TODO: Update    
    def copying_complete(
            self,
            event_type: FileSystemEvents,
            src_path: Path,
            dest_path: Path
    ) -> bool:
        """
        Checks if the copying of a file is complete based on its size and
        triggers appropriate actions.

        Args:
            event_type (FileSystemEvents): The type of file system event (e.g.,
                CREATED, MODIFIED).
            src_path (Path): The path to the source file being checked.
            dest_path (Path): The destination path where the file is being copied.

        Returns:
            None
        """
        if not src_path.exists():
            return
        current_size = self.get_file_size(src_path)
        previous_size = self.copying_files.get(src_path, 0)
        if current_size == previous_size:
            if event_type == FileSystemEvents.CREATED.value:
                with contextlib.suppress(PermissionError):
                    self.copy_file(src_path, dest_path)
            elif event_type == FileSystemEvents.MODIFIED.value:
                self.sync_file(src_path, dest_path)
        else:
            self.copying_files[src_path] = current_size
            self.start_copying_timer(event_type, src_path, dest_path)

    # TODO: Update    
    def copy_directory(self, event_type: FileSystemEvents, src_path):
        """
        Copies a directory from the source to the destination, preserving the
            directory structure.

        Args:
            event_type (FileSystemEvents): The type of file system event
                triggering the copy.
            src_path (Path): The source directory path to be copied.
        """
        relative_path = src_path.relative_to(self.source)
        destination_dir = self.destination / relative_path
        destination_dir.mkdir(parents=True, exist_ok=True)

        for file_path in get_files(src_path, time_type=None):
            if file_path.is_file():
                self.track_file_copy(event_type, file_path)

    # TODO: Update
    def copy_file(self, src_path: Path, dest_path: Path) -> None:
        """
        Copies a file from the source path to the destination path, preserving
        metadata.

        Args:
            src_path (Path): The source file path to copy.

        Raises:
            PermissionError: If there is a permission error during the copy.
        """
        relative_path = src_path.relative_to(self.source)
        destination_file = dest_path / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src_path, destination_file)
            self.untrack_file_copy(src_path)
        except PermissionError:
            raise PermissionError(
                f"Permission denied: {src_path} -> {destination_file}"
            )

    # TODO: Update
    def delete(self, file_path: Path) -> None:
        """
        Deletes a file or directory at the given source path from the destination.

        Args:
            file_path (Path): The source path of the file or directory to delete.

        Returns:
            None
        """
        relative_path = src_path.relative_to(self.source)
        destination = self.destination / relative_path
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            shutil.rmtree(file_path, ignore_errors=True)

    @abstractmethod
    def get_src_dest_paths(
        self,
        origin: Path,
        src_path: Path
    ) -> tuple[Path, Path]:
        ...

    # TODO: Update
    def get_file_size(self, src_path: Path, delay: float = 0.1) -> int:
        """
        Get the size of the file at the given path.

        Args:
            src_path (Path): The path to the source file.
            delay (float, optional): The delay in seconds to wait if a
                PermissionError occurs. Defaults to 0.1.

        Returns:
            int: The size of the file in bytes. Returns 0 if the file is not
                found or a PermissionError occurs.
        """
        try:
            with src_path.open('rb') as f:
                f.seek(0, 2)  # Move the cursor to the end of the file
                return f.tell()  # Get the current position of the cursor
        except PermissionError:
            time.sleep(delay)
        return 0

    # TODO: Update
    def rename(self, event: FileSystemEvents) -> None:
        """
        Renames a file or directory based on the provided FileSystemEvents.

        Args:
            event (FileSystemEvents): The event containing source and
                destination paths.
        """
        src_path = Path(event.src_path.replace(str(self.source), ''))
        dest_path = Path(event.dest_path.replace(str(self.source), ''))
        shutil.move(
            self.destination / src_path.relative_to('\\'),
            self.destination / dest_path.relative_to('\\')
        )

    # TODO: Update
    def set_debounce_interval(self, interval: float) -> None:
        """
        Sets the debounce interval for file system events.

        Args:
            interval (float): The interval in seconds to debounce file system
                events.
        """
        self.debounce_interval = interval

    # TODO: Update
    def start_copying_timer(
            self,
            event_type: FileSystemEvents,
            src_path: Path,
            dest_path: Path
    ) -> None:
        """
        Starts a timer to debounce file system events and check if copying is
            complete.

        Args:
            event_type (FileSystemEvents): The type of file system event.
            src_path (Path): The source path of the file being copied.

        Raises:
            Exception: If there is an error starting the copying timer.
        """
        if src_path in self.copying_timers:
            self.copying_timers[src_path].cancel()
        self.copying_timers[src_path] = threading.Timer(
            self.debounce_interval,
            self.copying_complete,
            [event_type, src_path, dest_path]
        )
        self.copying_timers[src_path].start()

    @abstractmethod
    def sync_file(self, src_path: Path, dest_path: Path) -> None:
        pass

    # TODO: Update
    def track_file_copy(
            self,
            event_type: FileSystemEvents,
            src_path: Path,
            dest_path: Path
    ) -> None:
        """
        Tracks the copying of a file by recording its size and starting a timer.
        Args:
            event_type (FileSystemEvents): The type of file system event.
            src_path (Path): The source path of the file being copied.
        Returns:
            None
        """
        if not src_path.exists():
            return

        self.copying_files[src_path] = self.get_file_size(src_path)
        self.start_copying_timer(event_type, src_path, dest_path)

    # TODO: Update
    def untrack_file_copy(self, src_path: Path) -> None:
        """
        Stops tracking the copying process of a file.

        Args:
            src_path (Path): The source path of the file to stop tracking.
        """
        if self.copying_files.get(src_path):
            del self.copying_files[src_path]
        if self.copying_timers.get(src_path):
            self.copying_timers[src_path].cancel()
            del self.copying_timers[src_path]

    def __repr__(self):
        return f'{self.__class__.__name__}(source={self.source}, ' \
            f'{self.destination})'

    def __str__(self):
        return f'{self.__class__.__name__}: Source={self.source}, ' \
            f'Destination={self.destination}'
