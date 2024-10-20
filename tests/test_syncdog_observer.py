import logging
import unittest
import tempfile
import shutil
from pathlib import Path
import threading

from PySide6 import QtCore, QtWidgets
from syncdog.constants import FileSystemEvents
from syncdog.syncdog_observer import SyncDogObserver
from watchdog.events import FileSystemEvent
from watchdog.events import LoggingEventHandler

from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_created = False
        self.folder_created = False
        self.file_modified = False
        self.file_moved = False
        self.file_deleted = False

    def dispatch(self, event):
        # print(f'Event received: {event}')
        self.on_any_event(event)

    def on_any_event(self, event: FileSystemEvents):
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.

        Returns:
            None
        """
        print(f'Event received: {event}')
        match event.event_type:
            case FileSystemEvents.CREATED.value:
                if event.is_directory:
                    self.folder_created = True
                else:
                    self.file_created = True
            case FileSystemEvents.DELETED.value:
                self.file_deleted = True
            case FileSystemEvents.MOVED.value:
                self.file_moved = True
            case FileSystemEvents.MODIFIED.value:
                self.file_modified = True


class TestSyncDogObserver(unittest.TestCase):
    def setUp(self):
        self.source = Path(tempfile.mkdtemp())
        self.destination = Path(tempfile.mkdtemp())
        self.handler = FileSystemEventHandler()
        self.observer = SyncDogObserver(
            directory=self.source, file_handler=self.handler)
        self.thread = threading.Thread(target=self.observer.run)

    def test_run(self):
        self.thread.start()
        # Allow some time for the observer to start
        self.thread.join(timeout=1)
        self.assertTrue(self.observer.is_running)

    def tearDown(self):
        self.observer.stop()
        shutil.rmtree(self.source)
        shutil.rmtree(self.destination)


if __name__ == "__main__":
    unittest.main()
