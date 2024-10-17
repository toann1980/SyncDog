from pathlib import Path
from logger import Logger
import os
import shutil
import time
import threading
from typing import Union

import bsdiff4
from getfiles import get_files
from watchdog.events import FileSystemEventHandler
from syncdog.constants import FileSystemEvents

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class BSDiffFileHandler(FileSystemEventHandler):
    def __init__(
            self,
            source: Union[str, Path],
            destination: Union[str, Path],
            debounce_interval: float = 1.25
    ) -> None:
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.debounce_interval = debounce_interval
        self.last_called = {
            'created': 0,
            'deleted': 0,
            'modified': 0,
            'moved': 0
        }
        self.copying_files = {}
        self.copying_timers = {}

    def on_any_event(self, event: FileSystemEvents):
        event_type = event.event_type
        src_path = Path(event.src_path)
        match event.event_type:
            case FileSystemEvents.CREATED.value:
                if event.is_directory:
                    self.copy_directory(event_type, src_path)
                else:
                    self.track_file_copy(event_type, src_path)
            case FileSystemEvents.DELETED.value:
                self.delete_file(src_path)
            case FileSystemEvents.MOVED.value:
                self.rename_object(event)
            case FileSystemEvents.MODIFIED.value:
                if self.copying_files.get(src_path):
                    return
                self.track_file_copy(event_type, src_path)

    def check_copying_complete(
            self,
            event_type: FileSystemEvents,
            src_path: Path
    ) -> None:
        if not src_path.exists():
            return
        current_size = self.get_file_size(src_path)
        previous_size = self.copying_files.get(src_path, 0)
        if current_size == previous_size:
            if event_type == FileSystemEvents.CREATED.value:
                self.copy_file(src_path)
            elif event_type == FileSystemEvents.MODIFIED.value:
                self.sync_file(src_path)
        else:
            self.copying_files[src_path] = current_size
            self.start_copying_timer(event_type, src_path)

    def copy_directory(self, event_type: FileSystemEvents, src_path):
        relative_path = src_path.relative_to(self.source)
        destination_dir = self.destination / relative_path
        destination_dir.mkdir(parents=True, exist_ok=True)

        for file_path in get_files(src_path, time_type=None):
            if file_path.is_file():
                self.track_file_copy(event_type, file_path)

    def copy_file(self, src_path: Path) -> None:
        relative_path = src_path.relative_to(self.source)
        destination_file = self.destination / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src_path, destination_file)
            self.untrack_file_copy(src_path)
        except FileNotFoundError:
            return
        except PermissionError:
            return

    def delete_file(self, src_path: Path) -> None:
        relative_path = src_path.relative_to(self.source)
        logger.debug(
            f'src_path is file: {src_path.is_file()}, '
            f'is dir: {src_path.is_dir()}'
        )
        destination = self.destination / relative_path
        if destination.is_file():
            if destination.exists():
                destination.unlink()
                logger.debug(f"Deleted file: {destination}")
        elif destination.is_dir():
            shutil.rmtree(destination, ignore_errors=True)
            logger.debug(f"Deleted directory: {destination}")

    def get_file_size(self, src_path: Path, delay: float = 0.1) -> int:
        try:
            with src_path.open('rb') as f:
                f.seek(0, 2)  # Move the cursor to the end of the file
                return f.tell()  # Get the current position of the cursor
        except FileNotFoundError:
            return 0
        except PermissionError:
            time.sleep(delay)
        return 0

    def rename_object(self, event: FileSystemEvents) -> None:
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
        try:
            if not src_path.exists():
                return
            relative_path = src_path.relative_to(self.source)
            dest_file = self.destination / relative_path
            diff_file = dest_file.with_suffix('.patch')
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
            # self.last_called[event.event_type] = 0
            logger.error(f"Error syncing file: {e}")

    def track_file_copy(
            self,
            event_type: FileSystemEvents,
            src_path: Path
    ) -> None:
        if not src_path.exists():
            return

        self.copying_files[src_path] = self.get_file_size(src_path)
        self.start_copying_timer(event_type, src_path)

    def untrack_file_copy(self, src_path: Path) -> None:
        if self.copying_files.get(src_path):
            del self.copying_files[src_path]
        if self.copying_timers.get(src_path):
            self.copying_timers[src_path].cancel()
            del self.copying_timers[src_path]
