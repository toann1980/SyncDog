import unittest
import tempfile
import shutil
from pathlib import Path
import threading

from syncdog.observer import SyncDogObserver

from watchdog.events import FileSystemEventHandler


class TestSyncDogObserver(unittest.TestCase):
    def setUp(self):
        self.source = Path(tempfile.mkdtemp())
        self.destination = Path(tempfile.mkdtemp())
        self.handler = FileSystemEventHandler()
        self.observer = SyncDogObserver(
            directory=self.source, handler=self.handler)
        self.thread = threading.Thread(target=self.observer.run)

    def test_run(self):
        self.thread.start()
        # Allow some time for the observer to start
        self.thread.join(timeout=1)
        self.assertTrue(self.observer.is_running)

    def test_run_multiple_directories(self):
        self.observer.set_directory([self.source, self.destination])
        self.thread.start()
        # Allow some time for the observer to start
        self.thread.join(timeout=1)
        self.assertTrue(self.observer.is_running)
        self.assertTrue(
            self.observer.directory, [self.source, self.destination]
        )

    def test_stop(self):
        self.thread.start()
        self.observer.stop()
        self.thread.join(timeout=1)
        self.assertFalse(self.observer.is_running)

    def test_set_directory(self):
        self.thread.start()
        self.assertEqual(self.observer.directory, self.source)
        self.observer.stop()
        self.thread.join(timeout=1)
        self.observer.set_directory(self.destination)
        self.assertEqual(self.observer.directory, self.destination)

    def test_set_directoryy_error(self):
        self.thread.start()
        self.assertEqual(self.observer.directory, self.source)
        self.thread.join(timeout=1)
        with self.assertRaises(RuntimeError):
            self.observer.set_directory(self.destination)

        self.assertEqual(self.observer.directory, self.source)
        print(f'observer is_running: {self.observer.is_running}')

    def test_set_handler(self):
        self.thread.start()
        self.assertEqual(self.observer.handler, self.handler)
        self.observer.stop()
        self.thread.join(timeout=1)
        new_handler = FileSystemEventHandler()
        self.observer.set_handler(new_handler)
        self.assertEqual(self.observer.handler, new_handler)

    def test_set_handler_when_running(self):
        self.thread.start()
        self.assertEqual(self.observer.handler, self.handler)
        self.thread.join(timeout=1)
        with self.assertRaises(RuntimeError):
            self.observer.set_handler(FileSystemEventHandler())

        self.assertEqual(self.observer.handler, self.handler)

    def test_repr(self):
        exp_repr = f"SyncDogObserver(directory={self.observer.directory!r}, " \
            f"handler={self.observer.handler!r})"
        self.assertEqual(repr(self.observer), exp_repr)

    def test_str_directory(self):
        self.assertEqual(
            str(self.observer),
            f"SyncDogObserver monitoring directory: {self.observer.directory}"
        )

    def test_str_no_directory(self):
        self.observer.directory = None
        self.assertEqual(
            str(self.observer),
            "SyncDogObserver not monitoring any directory."
        )

    def tearDown(self):
        self.observer.stop()
        shutil.rmtree(self.source)
        shutil.rmtree(self.destination)
