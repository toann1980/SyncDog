import unittest
import tempfile
import time
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from syncdog.file_handler import FileHandler
from syncdog.constants import FileSystemEvents
from watchdog.events import FileSystemEvent


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.source = Path(self.temp_dir) / "source"
        self.destination = Path(self.temp_dir) / "destination"
        self.patch_path = self.destination / '.syncdog'
        self.destination.mkdir()
        self.source.mkdir()
        self.patch_path.mkdir()
        self.handler = FileHandler(
            source=self.source, destination=self.destination)
        self.handler.patch_path = self.patch_path

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_on_any_event_source_none(self):
        """
        Test the `on_any_event` method when the source is None.

        This test verifies that when the handler's source is set to None,
        the `on_any_event` method does not call any of the file operation methods
        (`copy_directory`, `track_file_copy`, `delete`, `rename`) regardless of
        the event type.
        """
        self.handler.source = None
        event = FileSystemEvent(src_path=str(self.source / "created_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_destination_none(self):
        """
        Test the `on_any_event` method when the destination is None.

        This test verifies that when the handler's destination is set to None,
        the `on_any_event` method does not call any of the file operation methods
        (`copy_directory`, `track_file_copy`, `delete`, `rename`) regardless of
        the event type.
        """
        self.handler.destination = None
        event = FileSystemEvent(src_path=str(self.source / "created_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_syncdog_in_path(self):
        event_path = self.source / ".syncdog" / "created_file.txt"
        event = FileSystemEvent(src_path=str(event_path))

        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_created_file(self):
        """
        Test the `on_any_event` method for handling a created file event.
        This test simulates a file creation event and verifies that the
        `track_file_copy` method is called exactly once with the correct event
        type and file path.
        """
        event = FileSystemEvent(src_path=str(self.source / "new_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = False

        with patch.object(self.handler, 'track_file_copy') as mock_track_copy:
            self.handler.on_any_event(event)
            mock_track_copy.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_on_any_event_created_directory(self):
        """
        Test the `on_any_event` method of the handler for a created directory
        event. This test simulates a directory creation event and verifies that
        the `copy_directory` method of the handler is called exactly once with
        the correct parameters.
        """
        event = FileSystemEvent(src_path=str(self.source / "new_directory"))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = True

        with patch.object(self.handler, 'copy_directory') as mock_copy_dir:
            self.handler.on_any_event(event)
            mock_copy_dir.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_on_any_event_deleted_file(self):
        """
        Test the handler's response to a file deletion event.
        This test simulates a file deletion event and verifies that the handler's
        `delete` method is called exactly once with the correct file path.
        """
        event = FileSystemEvent(src_path=str(self.source / "deleted_file.txt"))
        event.event_type = FileSystemEvents.DELETED.value

        with patch.object(self.handler, 'delete') as mock_delete:
            self.handler.on_any_event(event)
            mock_delete.assert_called_once_with(Path(event.src_path))

    def test_on_any_event_moved_file(self):
        """
        Test the `on_any_event` method for handling a moved file event.
        This test simulates a file system event where a file is moved and
        verifies that the `rename` method of the handler is called exactly once
        with the event as its argument.
        """
        event = FileSystemEvent(src_path=str(self.source / "moved_file.txt"))
        event.event_type = FileSystemEvents.MOVED.value

        with patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_rename.assert_called_once_with(event)

    def test_on_any_event_modified_file(self):
        """
        Test the handler's response to a modified file event.
        This test simulates a file modification event and verifies that the 
        handler's 'track_file_copy' method is called with the correct parameters.
        """
        event = FileSystemEvent(src_path=str(
            self.source / "modified_file.txt"))
        event.event_type = FileSystemEvents.MODIFIED.value

        with patch.object(self.handler, 'track_file_copy') as mock_track_copy:
            self.handler.on_any_event(event)
            mock_track_copy.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_change_destination(self):
        """
        Test the change_destination method to ensure it correctly updates the
        handler's destination and manages the '.syncdog' directory as expected.
        """
        new_destination = Path(self.temp_dir) / "new_destination"
        new_destination.mkdir()
        self.handler.change_destination(new_destination)

        self.assertFalse((self.destination / '.syncdog').exists())

        self.assertEqual(self.handler.destination, new_destination)
        self.assertEqual(self.handler.patch_path, new_destination / '.syncdog')
        self.assertTrue((new_destination / '.syncdog').exists())

    def test_change_destination_patch_path_exists(self):
        """
        Test the change_destination method to ensure it correctly updates the
        destination and patch path, and removes the old patch path.
        """
        new_destination = Path(self.temp_dir) / "new_destination"
        new_destination.mkdir()

        old_patch_path = self.patch_path
        self.handler.change_destination(new_destination)

        self.assertEqual(self.handler.destination, new_destination)
        self.assertEqual(self.handler.patch_path, new_destination / '.syncdog')

        self.assertFalse(old_patch_path.exists())
        self.assertTrue((new_destination / '.syncdog').exists())

    def test_change_source(self):
        """
        Test the change_source method to ensure it updates the handler's source
        directory.
        """
        new_source = Path(self.temp_dir) / "new_source"
        new_source.mkdir()

        self.handler.change_source(new_source)

        self.assertEqual(self.handler.source, new_source)

    def test_check_copying_complete_created(self):
        """
        Test the `check_copying_complete` method for handling file creation
        events. This test verifies that a file is correctly copied from the
        source to the destination when a file creation event is detected.
        """
        temp_file = self.source / "test_file.txt"
        data = b"Hello, World!"
        with temp_file.open('wb') as f:
            f.write(data)

        self.handler.copying_files[temp_file] = len(data)

        self.handler.check_copying_complete(
            FileSystemEvents.CREATED.value, temp_file)

        copied_file = self.destination / temp_file.name
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_bytes(), data)

    def test_check_copying_complete_modified(self):
        """
        Test the check_copying_complete method for handling a modified file
        event. This test verifies that when a file is modified, it is correctly
        copied to the destination, and the copied file's content matches the
        original data.
        """
        temp_file = self.source / "test_file.txt"
        data = b"Hello, World!"
        with temp_file.open('wb') as f:
            f.write(data)
        synced_file = self.destination / temp_file.name
        synced_file.touch()
        self.handler.copying_files[temp_file] = len(data)

        self.handler.check_copying_complete(
            FileSystemEvents.MODIFIED.value, temp_file)

        self.assertTrue(synced_file.exists())
        self.assertEqual(synced_file.read_bytes(), data)

    def test_check_copying_complete_in_progress(self):
        """
        Test that a file is still marked as being copied when its size is less
        than expected.
        """
        temp_file = self.source / "test_file.txt"
        data = b"Hello, World!"
        with temp_file.open('wb') as f:
            f.write(data)

        self.handler.copying_files[temp_file] = len(data) - 1
        self.handler.check_copying_complete(
            FileSystemEvents.MODIFIED.value, temp_file)

        # Verify that the file is still being copied
        self.assertIn(temp_file, self.handler.copying_files)


if __name__ == "__main__":
    unittest.main()
