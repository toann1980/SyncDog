import unittest
import tempfile
import time
import shutil
from pathlib import Path
from unittest.mock import call, patch, MagicMock

from syncdog.file_handler import FileHandler
from syncdog.constants import FileSystemEvents
from watchdog.events import FileSystemEvent


class TestFileHandler(unittest.TestCase):
    def setUp(self) -> None:
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

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_on_any_event_source_none(self) -> None:
        """
        Test the `on_any_event` method when the source is None.

        This test verifies that when the handler's source is set to None,
        the `on_any_event` method does not call any of the file operation
        methods (`copy_directory`, `track_file_copy`, `delete`, `rename`)
        regardless of the event type.
        """
        self.handler.source = None
        event = FileSystemEvent(src_path=str(self.source / "created_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as \
                mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_destination_none(self) -> None:
        """
        Test the `on_any_event` method when the destination is None.

        This test verifies that when the handler's destination is set to None,
        the `on_any_event` method does not call any of the file operation
        methods (`copy_directory`, `track_file_copy`, `delete`, `rename`)
        regardless of the event type.
        """
        self.handler.destination = None
        event = FileSystemEvent(src_path=str(self.source / "created_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as \
                mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_syncdog_in_path(self) -> None:
        event_path = self.source / ".syncdog" / "created_file.txt"
        event = FileSystemEvent(src_path=str(event_path))

        event.event_type = FileSystemEvents.CREATED.value
        with patch.object(self.handler, 'copy_directory') as mock_copy_dir, \
                patch.object(self.handler, 'track_file_copy') as \
                mock_track_copy, \
                patch.object(self.handler, 'delete') as mock_delete, \
                patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_track_copy.assert_not_called()
            mock_copy_dir.assert_not_called()
            mock_delete.assert_not_called()
            mock_rename.assert_not_called()

    def test_on_any_event_created_file(self) -> None:
        """
        Verifies that the `track_file_copy` method is called exactly once with
        the correct event type and file path.
        """
        event = FileSystemEvent(src_path=str(self.source / "new_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = False

        with patch.object(self.handler, 'track_file_copy') as mock_track_copy:
            self.handler.on_any_event(event)
            mock_track_copy.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_on_any_event_created_directory(self) -> None:
        """
        Test the `on_any_event` method for handling a created directory event.
        """
        event = FileSystemEvent(src_path=str(self.source / "new_directory"))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = True

        with patch.object(self.handler, 'copy_directory') as mock_copy_dir:
            self.handler.on_any_event(event)
            mock_copy_dir.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_on_any_event_deleted_file(self) -> None:
        """
        Test the handler's response to a file deletion event.
        This test simulates a file deletion event and verifies that the
        handler's `delete` method is called exactly once with the correct file
        path.
        """
        event = FileSystemEvent(src_path=str(self.source / "deleted_file.txt"))
        event.event_type = FileSystemEvents.DELETED.value

        with patch.object(self.handler, 'delete') as mock_delete:
            self.handler.on_any_event(event)
            mock_delete.assert_called_once_with(Path(event.src_path))

    def test_on_any_event_moved_file(self) -> None:
        """
        This test verifies that the `rename` method is called once with the
        correct event when a file is moved.
        """
        event = FileSystemEvent(src_path=str(self.source / "moved_file.txt"))
        event.event_type = FileSystemEvents.MOVED.value

        with patch.object(self.handler, 'rename') as mock_rename:
            self.handler.on_any_event(event)
            mock_rename.assert_called_once_with(event)

    def test_on_any_event_modified_file(self) -> None:
        """
        Test that the handler correctly tracks a modified file event.
        """
        event = FileSystemEvent(src_path=str(
            self.source / "modified_file.txt"))
        event.event_type = FileSystemEvents.MODIFIED.value

        with patch.object(self.handler, 'track_file_copy') as mock_track_copy:
            self.handler.on_any_event(event)
            mock_track_copy.assert_called_once_with(
                event.event_type, Path(event.src_path))

    def test_on_any_event_modified_file_being_copied(self) -> None:
        """
        Test that the handler does not track a file copy event when the file is
        being copied.
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

    def test_change_destination(self) -> None:
        """
        Test the change_destination method to ensure it correctly updates the
        handler's destination directory and associated paths.
        """
        new_destination = Path(self.temp_dir) / "new_destination"
        new_destination.mkdir()
        self.handler.change_destination(new_destination)

        self.assertFalse((self.destination / '.syncdog').exists())

        self.assertEqual(self.handler.destination, new_destination)
        self.assertEqual(self.handler.patch_path, new_destination / '.syncdog')
        self.assertTrue((new_destination / '.syncdog').exists())

    def test_change_destination_patch_path_exists(self) -> None:
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

    def test_change_source(self) -> None:
        """
        Test the change_source method to ensure it updates the handler's source
        directory.
        """
        new_source = Path(self.temp_dir) / "new_source"
        new_source.mkdir()

        self.handler.change_source(new_source)

        self.assertEqual(self.handler.source, new_source)

    def test_check_copying_complete_created(self) -> None:
        """
        This test verifies that when a file is marked as created, it is
        correctly copied to the destination and the copied file's content
        matches the original file's data.
        """
        self.handler.copying_files[self.test_file] = len(self.test_file_data)

        self.handler.check_copying_complete(
            FileSystemEvents.CREATED.value, self.test_file)

        copied_file = self.destination / self.test_file.name
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_bytes(), self.test_file_data)

    def test_check_copying_complete_modified(self) -> None:
        """
        Test the method for handling a modified file event.
        """
        synced_file = self.destination / self.test_file.name
        synced_file.touch()
        self.handler.copying_files[self.test_file] = len(self.test_file_data)

        self.handler.check_copying_complete(
            FileSystemEvents.MODIFIED.value, self.test_file)

        self.assertTrue(synced_file.exists())
        self.assertEqual(synced_file.read_bytes(), self.test_file_data)

    def test_check_copying_complete_in_progress(self) -> None:
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
        Test the method to ensure it correctly copies a directory from the
        source to the destination.
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
        time.sleep(1)
        dest_dir = self.destination / source_dir.name
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / file1.name).exists())
        self.assertTrue((dest_dir / file2.name).exists())

    def test_copy_file_permission_error(self) -> None:
        """
        Test the copy_file method when the source file has permission issues.
        """
        with patch('shutil.copy2', side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.handler.copy_file(self.test_file)

    def test_delete_file(self) -> None:
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

    def test_delete_directory(self) -> None:
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

    def test_get_file_size(self) -> None:
        """
        Test that get_file_size returns the correct size of the file.
        """
        with open(self.test_file, 'wb') as f:
            f.write(self.test_file_data)

        size = self.handler.get_file_size(self.test_file)
        self.assertEqual(size, len(self.test_file_data))

    @patch('pathlib.Path.open')
    def test_get_file_size_permission_error(self, mock_open: MagicMock) -> None:
        """
        Test that get_file_size returns 0 if a PermissionError occurs.
        """
        mock_open.side_effect = PermissionError
        size = self.handler.get_file_size(self.test_file)
        self.assertEqual(size, 0)

    def test_rename(self) -> None:
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
    def test_start_copying_timer(self, mock_timer: MagicMock) -> None:
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

    def test_track_file_copy_not_exists(self) -> None:
        """
        Test the track_file_copy method when the source file does not exist.
        """
        src_file = self.source / "non_existent_file.txt"
        self.handler.track_file_copy(FileSystemEvents.CREATED.value, src_file)
        self.assertNotIn(src_file, self.handler.copying_files)

    def test_sync_file_success(self) -> None:
        """
        Test the sync_file method for successfully syncing a file.
        """
        self.handler.sync_file(self.test_file)
        time.sleep(1)

        dest_file = self.destination / self.test_file.relative_to(self.source)
        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.read_bytes(), self.test_file_data)

    def test_sync_file_not_exists(self) -> None:
        """
        Test the sync_file method for a source file that does not exist.
        """
        src_file = self.source / "non_existent_file.txt"
        self.handler.sync_file(src_file)

        dest_file = self.destination / src_file.relative_to(self.source)
        self.assertFalse(dest_file.exists())

    @patch('syncdog.file_handler.os.makedirs')
    def test_sync_file_creates_directory(
            self,
            mock_makedirs: MagicMock
    ) -> None:
        """
        Test the sync_file method for creating a directory if the source path is
        a directory.
        """
        src_dir = self.source / "test_dir"
        src_dir.mkdir(parents=True, exist_ok=True)

        self.handler.sync_file(src_dir)

        mock_makedirs.assert_called_once_with(
            self.destination / src_dir.relative_to(self.source), exist_ok=True)

    @patch('syncdog.file_handler.bsdiff4.file_diff')
    @patch('syncdog.file_handler.bsdiff4.file_patch')
    def test_sync_file_creates_patch(
            self,
            mock_file_patch: MagicMock,
            mock_file_diff: MagicMock
    ) -> None:
        """
        Test the sync_file method for creating a patch when the destination
        file exists.
        """
        dest_file = self.destination / self.test_file.relative_to(self.source)
        with dest_file.open('wb') as f:
            f.write(b"Old content")

        self.handler.sync_file(self.test_file)
        mock_file_diff.assert_called_once()
        mock_file_patch.assert_called_once()

    @patch('syncdog.file_handler.os.remove')
    def test_sync_file_removes_larger_dest_file(
            self,
            mock_remove: MagicMock
    ) -> None:
        """
        Test the sync_file method for removing the destination file if it is
        larger than the source file.
        """
        dest_file = self.destination / self.test_file.relative_to(self.source)
        patch_file = self.patch_path / \
            self.test_file.relative_to(self.source).with_suffix('.patch')
        patch_file.touch()
        with dest_file.open('wb') as f:
            f.write(b"Hello, World! Hello, World!")

        self.handler.sync_file(self.test_file)
        mock_remove.assert_has_calls([call(dest_file), call(patch_file)])

    @patch('syncdog.file_handler.FileHandler.track_file_copy')
    def test_sync_file_ioerror(self, mock_track_file_copy: MagicMock) -> None:
        """
        Test the sync_file method for handling IOError.
        """
        mock_track_file_copy.side_effect = IOError("Test IOError")
        self.handler.sync_file(self.test_file)
        mock_track_file_copy.assert_called_once_with(
            FileSystemEvents.CREATED.value, self.test_file)

    @patch('syncdog.file_handler.FileHandler.track_file_copy')
    def test_sync_file_permissionerror(
            self,
            mock_track_file_copy: MagicMock
    ) -> None:
        """
        Test the sync_file method for handling PermissionError.
        """
        mock_track_file_copy.side_effect = PermissionError(
            "Test PermissionError")
        self.handler.sync_file(self.test_file)
        mock_track_file_copy.assert_called_once_with(
            FileSystemEvents.CREATED.value, self.test_file)

    @patch('syncdog.file_handler.Logger.error')
    def test_sync_file_logs_error(self, mock_logger_error: MagicMock) -> None:
        """
        Test the sync_file method for logging an error if an exception occurs.
        """
        with patch.object(
                self.handler,
                'track_file_copy',
                side_effect=Exception("Test exception")
        ):
            self.handler.sync_file(self.test_file)

        mock_logger_error.assert_called_once_with(
            "Error syncing file: Test exception")
