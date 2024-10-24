from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import time
import threading

from logger import Logger
from syncdog.constants import FileSystemEvents

import bsdiff4
from watchdog.events import FileSystemEventHandler

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class BaseHandler(FileSystemEventHandler, ABC):
    def __init__(
            self,
            debounce_interval: float = 0.5
    ) -> None:
        super().__init__()
        self.debounce_interval = debounce_interval
        self.working_files = {}
        self.working_timers = {}

    @abstractmethod
    def on_any_event(self, event: FileSystemEvents) -> None:
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    def create_complete(
            self,
            event_type: FileSystemEvents,
            source: Path,
            source_path: Path,
            dest: Path,
            patch_path: Path
    ) -> bool:
        """
        Checks if the copying of a file is complete based on its size and
        triggers appropriate actions.

        Args:
            event_type (FileSystemEvents): The type of file system event (e.g.,
                CREATED, MODIFIED).
            source (Path): The source directory.
            source_path (Path): The path to the source file.
            dest (Path): The path where the file is being copied.
            patch_path (Path): The path where patch files are stored.

        Returns:
            bool: True if the file copy is complete, False otherwise.
        """
        if not source_path.exists():
            return
        current_size = self.get_file_size(source_path)
        previous_size = self.working_files.get(source_path, 0)
        if current_size == previous_size:
            if event_type == FileSystemEvents.CREATED.value:
                try:
                    self.create_file(source, source_path, dest)
                except PermissionError:
                    self.track_work_file(
                        event_type, source, source_path, dest, patch_path)
            elif event_type == FileSystemEvents.MODIFIED.value:
                self.sync_file(source, source_path, dest, patch_path)
        else:
            self.working_files[source_path] = current_size
            self.start_working_timer(
                event_type, source, source_path, dest, patch_path)

    def create_directory(
        self,
        source: Path,
        source_path: Path,
        dest: Path
    ) -> None:
        """
        Creates a directory at the destination path.

        Args:
            source (Path): The source directory.
            source_path (Path): The path to the source directory.
            dest (Path): The destination directory path.
        """
        dir = self.get_dest_path(source, source_path, dest)
        dir.mkdir(parents=True, exist_ok=True)

    def create_file(self, source: Path, source_path: Path, dest: Path) -> None:
        """
        Copies a file from the source path to the destination path, preserving
        metadata.

        Args:
            source (Path): The source directory.
            source_path (Path): The source file path to copy.
            dest (Path): The destination directory path.

        Raises:
            PermissionError: If there is a permission error during the copy.
        """
        dest_path = self.get_dest_path(source, source_path, dest)
        if not dest_path.parent.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(source_path, dest_path)
            self.untrack_work_file(source_path)
        except PermissionError:
            raise PermissionError(
                f"Permission denied: {source_path} -> {dest_path}"
            )

    def delete(self, source: Path, source_path: Path, dest: Path) -> None:
        """
        Deletes a file or directory at the given destination path.

        Args:
            source (Path): The source directory.
            source_path (Path): The path to the source file or directory.
            dest (Path): The destination directory path.
        """
        dest_path = self.get_dest_path(source, source_path, dest)
        if not dest_path.exists():
            return

        if dest_path.is_file():
            dest_path.unlink()
        elif dest_path.is_dir():
            shutil.rmtree(dest_path, ignore_errors=True)

    def get_dest_path(
        self,
        source: Path,
        source_path: Path,
        dest: Path
    ) -> Path:
        """
        Constructs the destination path based on the source and destination
        directories.

        Args:
            source (Path): The source directory.
            source_path (Path): The path to the source file or directory.
            dest (Path): The destination directory path.

        Returns:
            Path: The constructed destination path.
        """
        return dest / source_path.relative_to(source)

    def get_file_size(self, source_path: Path, delay: float = 0.1) -> int:
        """
        Get the size of the file at the given path.

        Args:
            source_path (Path): The path to the source file.
            delay (float, optional): The delay in seconds to wait if a
                PermissionError occurs. Defaults to 0.2.

        Returns:
            int: The size of the file in bytes. Returns 0 if the file is not
                found or a PermissionError occurs.
        """
        try:
            with source_path.open('rb') as f:
                f.seek(0, 2)  # Move the cursor to the end of the file
                return f.tell()  # Get the current position of the cursor
        except PermissionError:
            time.sleep(delay)
        return 0

    def rename(self, event: FileSystemEvents, source: Path, dest: Path) -> None:
        """
        Renames a file or directory based on the provided FileSystemEvents.

        Args:
            event (FileSystemEvents): The event containing source and
                destination paths.
            source (Path): The source directory.
            dest (Path): The destination directory path.

        Note:
            Do not use Path.rename() as it does not work across different OSes.
        """
        original_name = Path(event.src_path.replace(str(source), ''))
        new_name = Path(event.dest_path.replace(str(source), ''))
        dest_path = dest / new_name.relative_to('\\')
        if dest_path.exists():
            return

        shutil.move(dest / original_name.relative_to('\\'), dest_path)

    def set_debounce_interval(self, interval: float) -> None:
        """
        Sets the debounce interval for file system events.

        Args:
            interval (float): The interval in seconds to debounce file system
                events.
        """
        self.debounce_interval = interval

    def start_working_timer(
            self,
            event_type: FileSystemEvents,
            source: Path,
            source_path: Path,
            dest_path: Path,
            patch_path: Path
    ) -> None:
        """
        Starts a timer to debounce file system events and check if copying is
        complete.

        Args:
            event_type (FileSystemEvents): The type of file system event.
            source (Path): The source directory.
            source_path (Path): The source path of the file being copied.
            dest_path (Path): The destination directory path.
            patch_path (Path): The path where patch files are stored.

        Raises:
            Exception: If there is an error starting the copying timer.
        """
        if source_path in self.working_timers:
            self.working_timers[source_path].cancel()
        self.working_timers[source_path] = threading.Timer(
            self.debounce_interval,
            self.create_complete,
            [event_type, source, source_path, dest_path, patch_path]
        )
        self.working_timers[source_path].start()

    def sync_file(
        self,
        source: Path,
        source_path: Path,
        dest: Path,
        patch_path: Path
    ) -> None:
        """
        Synchronizes a file from the source path to the destination path.

        Args:
            source (Path): The source directory.
            source_path (Path): The source file path to be synchronized.
            dest (Path): The destination directory path.
            patch_path (Path): The path where patch files are stored.
        """
        try:
            if not source_path.exists():
                return
            relative_path = source_path.relative_to(source)
            dest_path = dest / relative_path
            diff_file = patch_path / relative_path.with_suffix('.patch')
            if source_path.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
                return
            elif not dest_path.exists():
                return self.track_work_file(
                    'created', source, source_path, dest, patch_path)
            elif dest_path.stat().st_size > source_path.stat().st_size:
                dest_path.unlink()
                if diff_file.exists():
                    diff_file.unlink()
                return self.track_work_file(
                    'created', source, source_path, dest, patch_path)
            bsdiff4.file_diff(
                src_path=str(dest_path),
                dst_path=str(source_path),
                patch_path=str(diff_file)
            )
            bsdiff4.file_patch(
                src_path=str(dest_path),
                dst_path=str(dest_path),
                patch_path=str(diff_file)
            )
            time.sleep(0.25)
            self.untrack_work_file(source_path)
            self.untrack_work_file(dest_path)
            return
        except PermissionError:
            pass
        except IOError:
            if not patch_path.exists():
                patch_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error syncing file: {e}")

        self.start_working_timer(
            'modified', source, source_path, dest, patch_path)

    def track_work_file(
            self,
            event_type: FileSystemEvents,
            source: Path,
            source_path: Path,
            dest: Path,
            patch_path: Path
    ) -> None:
        """
        Tracks the copying of a file by recording its size and starting a timer.

        Args:
            event_type (FileSystemEvents): The type of file system event.
            source (Path): The source directory.
            source_path (Path): The source path of the file being copied.
            dest (Path): The destination directory path.
            patch_path (Path): The path where patch files are stored.
        """
        if not source_path.exists():
            return

        self.working_files[source_path] = self.get_file_size(source_path)
        self.start_working_timer(
            event_type, source, source_path, dest, patch_path)

    def untrack_work_file(self, source_path: Path) -> None:
        """
        Stops tracking the copying process of a file.

        Args:
            source_path (Path): The source path of the file to stop tracking.
        """
        if self.working_files.get(source_path):
            del self.working_files[source_path]
        if self.working_timers.get(source_path):
            self.working_timers[source_path].cancel()
            del self.working_timers[source_path]
