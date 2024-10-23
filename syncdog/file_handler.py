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
from syncdog.base_handler import BaseHandler

from syncdog.constants import FileSystemEvents

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class FileHandler(BaseHandler):
    """
    FileHandler class for handling file system events and synchronizing files
    between a source and destination directory.

    Attributes:
        source (Union[str, Path]): The source directory to monitor.
        destination (Union[str, Path]): The destination directory to sync files
            to.
        debounce_interval (float): The interval in seconds to debounce file
            system events.
        copying_files (dict): A dictionary to track files being copied and their
            sizes.
        copying_timers (dict): A dictionary to track timers for debouncing file
            system events.
        patch_path (Path): The path to the patch directory used for file
            synchronization.

    Methods:
        on_any_event(event: FileSystemEvents):
        change_destination(dest: Union[str, Path]) -> None:
        change_source(source: Union[str, Path]) -> None:
        check_copying_complete(event_type: FileSystemEvents, src_path: Path) ->
            None:
            Checks if the copying of a file is complete based on its size and
            triggers appropriate actions.
        cleanup() -> None:
            Cleans up the patch directory.
        copy_directory(event_type: FileSystemEvents, src_path: Path) -> None:
            Copies a directory from the source to the destination, preserving
            the directory structure.
        copy_file(src_path: Path) -> None:
            Copies a file from the source path to the destination path,
            preserving metadata.
        delete(src_path: Path) -> None:
        get_file_size(src_path: Path, delay: float = 0.1) -> int:
            Gets the size of the file at the given path.
        rename(event: FileSystemEvents) -> None:
        start_copying_timer(event_type: FileSystemEvents, src_path: Path) ->
            None:
            Starts a timer to debounce file system events and check if copying
            is complete.
        sync_file(src_path: Path) -> None:
        track_file_copy(event_type: FileSystemEvents, src_path: Path) -> None:
        untrack_file_copy(src_path: Path) -> None:
    """

    def __init__(
            self,
            source: Union[str, Path] = None,
            destination: Union[str, Path] = None,
            debounce_interval: float = 0.50
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

    def cleanup(self) -> None:
        if self.patch_path and self.patch_path.exists():
            shutil.rmtree(self.patch_path)
            self.patch_path = None

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

    def get_src_dest_paths(
        self,
        origin: Path,
        src_path: Path
    ) -> tuple[Path, Path]:
        relative_path = src_path.relative_to(origin)
        destination = self.destination / relative_path
        
        
    
    def sync_file(self, src_path: Path, dest_path: Path) -> None:
        """
        Synchronizes a file from the source path to the destination path.

        Args:
            src_path (Path): The source file path to be synchronized.

        Returns:
            None
        """
        try:
            if not src_path.exists():
                return
            relative_path = src_path.relative_to(self.source)
            dest_file = self.destination / relative_path
            diff_file = self.patch_path / relative_path.with_suffix('.patch')
            if src_path.is_dir():
                os.makedirs(dest_file, exist_ok=True)
                return
            elif not dest_file.exists():
                return self.track_file_copy('created', src_path)
            elif dest_file.stat().st_size > src_path.stat().st_size:
                os.remove(dest_file)
                if diff_file.exists():
                    os.remove(diff_file)
                return self.track_file_copy('created', src_path)
            bsdiff4.file_diff(
                src_path=str(dest_file),
                dst_path=str(src_path),
                patch_path=str(diff_file)
            )
            bsdiff4.file_patch(
                src_path=str(dest_file),
                dst_path=str(dest_file),
                patch_path=str(diff_file)
            )
            self.untrack_file_copy(src_path)
        except PermissionError:
            pass
        except IOError:
            pass
        except Exception as e:
            logger.error(f"Error syncing file: {e}")