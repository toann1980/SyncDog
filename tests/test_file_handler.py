import unittest
import tempfile
import time
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

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
        self.test_file = self.source / "test_file.txt"
        self.test_file_data = b"Hello, World!"
        with self.test_file.open('wb') as f:
            f.write(self.test_file_data)

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

    def test_on_any_event_modified_file_being_copied(self):
        """
        Test the `on_any_event` method for handling a modified file event
        when the file is currently being copied. This test verifies that
        the `track_file_copy` method is not called if the file is in the
        `copying_files` dictionary.
        """
        event = FileSystemEvent(
            src_path=str(self.source / "modified_file.txt"))
        event.event_type = FileSystemEvents.MODIFIED.value

        # Simulate that the file is currently being copied
        self.handler.copying_files[Path(event.src_path)] = \
            len(self.test_file_data)

        with patch.object(self.handler, 'track_file_copy') as mock_track_copy:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()

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
        self.handler.copying_files[self.test_file] = len(self.test_file_data)

        self.handler.check_copying_complete(
            FileSystemEvents.CREATED.value, self.test_file)

        copied_file = self.destination / self.test_file.name
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_bytes(), self.test_file_data)

    def test_check_copying_complete_modified(self):
        """
        Test the check_copying_complete method for handling a modified file
        event. This test verifies that when a file is modified, it is correctly
        copied to the destination, and the copied file's content matches the
        original data.
        """
        synced_file = self.destination / self.test_file.name
        synced_file.touch()
        self.handler.copying_files[self.test_file] = len(self.test_file_data)

        self.handler.check_copying_complete(
            FileSystemEvents.MODIFIED.value, self.test_file)

        self.assertTrue(synced_file.exists())
        self.assertEqual(synced_file.read_bytes(), self.test_file_data)

    def test_check_copying_complete_in_progress(self):
        """
        Test that a file is still marked as being copied when its size is less
        than expected.
        """
        self.handler.copying_files[self.test_file] = \
            len(self.test_file_data) - 1
        self.handler.check_copying_complete(
            FileSystemEvents.MODIFIED.value, self.test_file)

        # Verify that the file is still being copied
        self.assertIn(self.test_file, self.handler.copying_files)

    def test_cleanup(self) -> None:
        """
        Test the cleanup method to ensure it removes the patch directory if it
        exists.
        """
        self.handler.cleanup()
        self.assertFalse(self.patch_path.exists())

    def test_copy_directory(self) -> None:
        """
        Test the copy_directory method to ensure it correctly copies a directory
        from the source to the destination.
        """
        source_dir = self.source / "test_dir"
        source_dir.mkdir()
        file1 = source_dir / "file1.txt"
        file2 = source_dir / "file2.txt"
        file1.touch()
        file2.touch()
        for file in [file1, file2]:
            with file.open('w') as f:
                f.write("Hello, World!")

        self.handler.copy_directory(FileSystemEvents.CREATED.value, source_dir)
        time.sleep(2)
        dest_dir = self.destination / source_dir.name
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / file1.name).exists())
        self.assertTrue((dest_dir / file2.name).exists())

    def test_copy_file_permission_error(self):
        """
        Test the copy_file method when the source file has permission issues.
        """
        with patch('shutil.copy2', side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.handler.copy_file(self.test_file)

    def test_delete_file(self):
        """
        Test the delete_file method to ensure it deletes the specified file from
        the destination directory.
        """
        src_file = self.source / self.test_file
        dest_file = self.destination / "test_file.txt"
        dest_file.touch()
        self.assertTrue(dest_file.exists())

        self.handler.delete(src_file)

        self.assertFalse(dest_file.exists())

    def test_delete_directory(self):
        """
        Test the deletion of a directory.
        This test verifies that a directory is properly deleted by the handler.
        """
        temp_dir = "test_dir"
        src_dir = self.source / temp_dir
        dest_dir = self.destination / temp_dir
        dest_dir.mkdir()
        self.assertTrue(dest_dir.exists())

        self.handler.delete(src_dir)

        self.assertFalse(dest_dir.exists())

    def test_get_file_size(self):
        """
        Test that get_file_size returns the correct size of the file.
        """
        with open(self.test_file, 'wb') as f:
            f.write(self.test_file_data)

        size = self.handler.get_file_size(self.test_file)
        self.assertEqual(size, len(self.test_file_data))

    @patch('pathlib.Path.open')
    def test_get_file_size_permission_error(self, mock_open):
        """
        Test that get_file_size returns 0 if a PermissionError occurs.
        """
        mock_open.side_effect = PermissionError
        size = self.handler.get_file_size(self.test_file)
        self.assertEqual(size, 0)

    def test_rename(self):
        """
        Test the rename method to ensure it correctly renames a file in the
        destination directory.
        """
        dest_file = self.destination / "test_file.txt"
        # Create the source and destination files
        dest_file.touch()
        self.assertTrue(dest_file.exists())

        new_dest_file = self.destination / "new_name.txt"

        # Simulate the rename event
        event = FileSystemEvent(
            src_path=str(self.test_file),
            dest_path=str(self.source / "new_name.txt")
        )
        event.event_type = FileSystemEvents.MOVED.value

        self.handler.rename(event)

        # Check that the old file no longer exists and the new file exists
        self.assertFalse(dest_file.exists())
        self.assertTrue(new_dest_file.exists())

    @patch('threading.Timer')
    def test_start_copying_timer(self, mock_timer):
        """
        Test the start_copying_timer method to ensure it correctly starts a
        timer for the given file system event and source path.
        """
        event_type = FileSystemEvents.CREATED.value
        self.handler.copying_timers = {}

        existing_timer = MagicMock()
        self.handler.copying_timers[self.test_file] = existing_timer

        # Call the method
        self.handler.start_copying_timer(event_type, self.test_file)

        # Check that the timer was started with the correct arguments
        mock_timer.assert_called_once_with(
            self.handler.debounce_interval,
            self.handler.check_copying_complete,
            [event_type, self.test_file]
        )
        self.assertIn(self.test_file, self.handler.copying_timers)
        mock_timer.return_value.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
