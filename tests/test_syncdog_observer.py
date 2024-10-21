import unittest
import tempfile
import shutil
from pathlib import Path
import threading

from syncdog.syncdog_observer import SyncDogObserver

from watchdog.events import FileSystemEventHandler


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

    def test_stop(self):
        self.thread.start()
        # Allow some time for the observer to start
        self.observer.stop()
        self.thread.join(timeout=1)
        self.assertFalse(self.observer.is_running)

    def test_change_directory(self):
        self.thread.start()
        self.assertEqual(self.observer.directory, self.source)
        self.observer.stop()
        self.thread.join(timeout=1)
        self.observer.change_directory(self.destination)
        self.assertEqual(self.observer.directory, self.destination)

    def test_change_directory_error(self):
        self.thread.start()
        self.assertEqual(self.observer.directory, self.source)
        self.thread.join(timeout=1)
        with self.assertRaises(RuntimeError):
            self.observer.change_directory(self.destination)

        self.assertEqual(self.observer.directory, self.source)
        print(f'observer is_running: {self.observer.is_running}')

    def tearDown(self):
        self.observer.stop()
        shutil.rmtree(self.source)
        shutil.rmtree(self.destination)
