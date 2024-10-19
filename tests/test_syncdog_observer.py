import logging
import unittest
import tempfile
import shutil
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from syncdog.constants import FileSystemEvents
from syncdog.syncdog_observer import SyncDogObserver
from watchdog.events import FileSystemEvent
from watchdog.events import LoggingEventHandler

from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_created = False
        self.folder_created = False
        self.file_modified = False
        self.file_moved = False
        self.file_deleted = False

    def dispatch(self, event):
        print(f'Event received: {event}')
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

    # def on_created(self, event):
    #     print(f'File created: {event.src_path}')

    # def on_deleted(self, event):
    #     print(f'File deleted: {event.src_path}')

    # def on_modified(self, event):
    #     print(f'File modified: {event.src_path}')

    # def on_moved(self, event):
    #     print(f'File moved: {event.src_path} to {event.dest_path}')


class TestSyncDogObserver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QtWidgets.QApplication.instance():
            cls.app = QtWidgets.QApplication([])
        else:
            cls.app = QtWidgets.QApplication.instance()

    def setUp(self):
        self.source = Path(tempfile.mkdtemp())
        self.destination = Path(tempfile.mkdtemp())
        self.handler = FileHandler()
        self.observer = SyncDogObserver(
            directory=self.source, file_handler=self.handler)
        # self.observer.start()

    def test_run(self):
        self.observer.start()
        self.observer.msleep(1000)
        self.assertTrue(self.observer.is_running())

    def test_stop(self):
        self.observer.start()
        self.observer.msleep(1000)
        self.observer.stop()
        self.observer.wait()
        self.assertFalse(self.observer.is_running())

    def tearDown(self):
        self.observer.stop()
        self.observer.wait()
        shutil.rmtree(self.source)
        shutil.rmtree(self.destination)

    @classmethod
    def tearDownClass(cls):
        if QtWidgets.QApplication.instance():
            cls.app.quit()
            QtCore.QCoreApplication.quit()


if __name__ == "__main__":
    unittest.main()
