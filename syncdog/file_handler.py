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


class FileHandler(FileSystemEventHandler):
    def __init__(
            self,
            source: Union[str, Path] = None,
            destination: Union[str, Path] = None,
            debounce_interval: float = 1.25
    ) -> None:
        super().__init__()
        self.source = Path(source) if isinstance(source, str) else source
        self.destination = Path(destination) if isinstance(destination, str) \
            else destination
        self.patch_path: Path = None

        self.debounce_interval = debounce_interval
        self.copying_files = {}
        self.copying_timers = {}

    def on_any_event(self, event: FileSystemEvents):
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.

        Returns:
            None
        """
        if self.source is None or self.destination is None:
            return

        src_path = Path(event.src_path)
        if '.syncdog' in src_path.parts:
            return

        match event.event_type:
            case FileSystemEvents.CREATED.value:
                if event.is_directory:
                    self.copy_directory(event.event_type, src_path)
                else:
                    self.track_file_copy(event.event_type, src_path)
            case FileSystemEvents.DELETED.value:
                self.delete(src_path)
            case FileSystemEvents.MOVED.value:
                self.rename(event)
            case FileSystemEvents.MODIFIED.value:
                if self.copying_files.get(src_path):
                    return
                self.track_file_copy(event.event_type, src_path)

    def change_destination(self, dest: Union[str, Path]) -> None:
        """
        Changes the destination directory to a new directory.

        Args:
            dest (Union[str, Path]): The new destination directory.

        Returns:
            None
        """
        if self.patch_path and self.patch_path.exists():
            shutil.rmtree(self.patch_path)
        self.destination = Path(dest) if isinstance(dest, str) else dest
        self.patch_path = self.destination / '.syncdog'
        os.makedirs(self.patch_path, exist_ok=True)

    def change_source(self, source: Union[str, Path]) -> None:
        """
        Changes the source directory to a new directory.

        Args:
            source (Union[str, Path]): The new source directory to monitor.

        Returns:
            None
        """
        self.source = Path(source) if isinstance(source, str) else source

    def check_copying_complete(
            self,
            event_type: FileSystemEvents,
            src_path: Path
    ) -> None:
        """
        Checks if the copying of a file is complete based on its size and
        triggers appropriate actions.

        Args:
            event_type (FileSystemEvents): The type of file system event (e.g.,
                CREATED, MODIFIED).
            src_path (Path): The path to the source file being checked.

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
                    self.copy_file(src_path)
            elif event_type == FileSystemEvents.MODIFIED.value:
                self.sync_file(src_path)
        else:
            self.copying_files[src_path] = current_size
            self.start_copying_timer(event_type, src_path)

    def cleanup(self) -> None:
        if self.patch_path.exists():
            shutil.rmtree(self.patch_path)

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

    def copy_file(self, src_path: Path) -> None:
        """
        Copies a file from the source path to the destination path, preserving
        metadata.

        Args:
            src_path (Path): The source file path to copy.

        Raises:
            PermissionError: If there is a permission error during the copy.
        """
        relative_path = src_path.relative_to(self.source)
        destination_file = self.destination / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src_path, destination_file)
            self.untrack_file_copy(src_path)
        except PermissionError:
            raise PermissionError(
                f"Permission denied: {src_path} -> {destination_file}"
            )

    def delete(self, src_path: Path) -> None:
        """
        Deletes a file or directory at the given source path from the destination.

        Args:
            src_path (Path): The source path of the file or directory to delete.

        Returns:
            None
        """
        relative_path = src_path.relative_to(self.source)
        destination = self.destination / relative_path
        if destination.is_file():
            destination.unlink()
        elif destination.is_dir():
            shutil.rmtree(destination, ignore_errors=True)

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

    def start_copying_timer(
            self,
            event_type: FileSystemEvents,
            src_path: Path
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
        try:
            if src_path in self.copying_timers:
                self.copying_timers[src_path].cancel()
            self.copying_timers[src_path] = threading.Timer(
                self.debounce_interval,
                self.check_copying_complete,
                [event_type, src_path]
            )
            self.copying_timers[src_path].start()
        except Exception as e:
            logger.error(f"Error starting copying timer: {e}")

    def sync_file(self, src_path: Path) -> None:
        """
        Synchronizes a file from the source path to the destination path.
        Args:
            src_path (Path): The source file path to be synchronized.
        Returns:
            None
        Raises:
            Exception: If an error occurs during the synchronization process.
        """
        try:
            if not src_path.exists():
                return
            relative_path = src_path.relative_to(self.source)
            dest_file = self.destination / relative_path
            diff_file = self.patch_path / relative_path.with_suffix('.patch')
            if not dest_file.exists():
                return self.track_file_copy('created', src_path)
            elif dest_file.stat().st_size > src_path.stat().st_size:
                os.remove(dest_file)
                if diff_file.exists():
                    os.remove(diff_file)
                return self.track_file_copy('created', src_path)
            elif src_path.is_dir():
                os.makedirs(dest_file, exist_ok=True)
                return
            # Create a diff file using bsdiff4
            bsdiff4.file_diff(
                src_path=str(dest_file),
                dst_path=str(src_path),
                patch_path=str(diff_file)
            )

            # Apply the diff file to the destination
            bsdiff4.file_patch(
                src_path=str(dest_file),
                dst_path=str(dest_file),
                patch_path=str(diff_file)
            )

            logger.debug(
                f"Synced file: {src_path.name} to {dest_file.name}"
            )
            self.untrack_file_copy(src_path)
        except Exception as e:
            logger.error(f"Error syncing file: {e}")

    def track_file_copy(
            self,
            event_type: FileSystemEvents,
            src_path: Path
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
        self.start_copying_timer(event_type, src_path)

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
