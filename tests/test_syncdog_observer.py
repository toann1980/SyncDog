import logging
import unittest
import tempfile
import shutil
from pathlib import Path
from syncdog.constants import FileSystemEvents
from syncdog.syncdog_observer import SyncDogObserver
from watchdog.events import FileSystemEvent


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

    def on_any_event(self, event: FileSystemEvents):
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.

        Returns:
            None
        """
        logging.debug(f'Event received: {event}')
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
        self.handler = FileHandler()
        self.observer = SyncDogObserver(
            directory=self.source, file_handler=self.handler)
        self.observer.start()

    def tearDown(self):
        self.observer.stop()
        self.observer.wait()
        shutil.rmtree(self.source)
        shutil.rmtree(self.destination)

    def test_create_file(self):
        test_file = self.source / "test_file.txt"
        test_file.touch()
        self.observer.msleep(1000)
        print(f'{test_file.exists()=}')
        self.assertTrue(self.handler.file_created)

    # def test_modify_file(self):
    #     test_file = self.source / "test_file.txt"
    #     test_file.write_text("Hello, SyncDog!")
    #     test_file.write_text("Hello, SyncDog! Modified")

    #     self.observer.msleep(500)

    #     self.assertTrue(self.handler.file_modified)

    # def test_delete_file(self):
    #     test_file = self.source / "test_file.txt"
    #     test_file.write_text("Hello, SyncDog!")
    #     test_file.unlink()

    #     self.observer.msleep(500)
    #     print(f'Handler: {self.handler.file_deleted}')
    #     self.assertTrue(self.handler.file_deleted)


if __name__ == "__main__":
    unittest.main()
