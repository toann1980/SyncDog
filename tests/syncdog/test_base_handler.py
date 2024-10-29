import unittest
import tempfile
import time
import shutil
from pathlib import Path
from unittest.mock import call, patch, MagicMock

from syncdog.base_handler import BaseHandler
from syncdog.constants import FileSystemEvents
from watchdog.events import FileSystemEvent


class ConcreteBaseHandler(BaseHandler):
    def on_any_event(self, event: FileSystemEvents) -> None:
        print(f"Event received: {event}")

    def cleanup(self) -> None:
        pass


class TestBaseHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.source = Path(self.temp_dir) / "source"
        self.dest = Path(self.temp_dir) / "destination"
        self.patch_path = self.dest / '.syncdog'
        self.dest.mkdir()
        self.source.mkdir()
        self.patch_path.mkdir()
        self.handler = ConcreteBaseHandler()
        self.test_file = self.source / "test_file.txt"
        self.test_file_data = b"Hello, World!"
        with self.test_file.open('wb') as f:
            f.write(self.test_file_data)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_create_complete_created(self) -> None:
        """
        Verifies when a file is marked as created, it is correctly copied to the
        destination and the copied file's content matches the original file's
        data.
        """
        self.handler.working_files[self.test_file] = len(self.test_file_data)

        self.handler.create_complete(
            FileSystemEvents.CREATED.value, self.source, self.test_file,
            self.dest, self.patch_path)

        copied_file = self.dest / self.test_file.name
        self.assertTrue(copied_file.exists())
        self.assertEqual(copied_file.read_bytes(), self.test_file_data)

    def test_create_complete_modified(self) -> None:
        """
        Test the method for handling a modified file event.
        """
        synced_file = self.dest / self.test_file.name
        synced_file.touch()
        self.handler.working_files[self.test_file] = len(self.test_file_data)

        self.handler.create_complete(
            FileSystemEvents.MODIFIED.value, self.source, self.test_file,
            self.dest, self.patch_path)

        self.assertTrue(synced_file.exists())
        self.assertEqual(synced_file.read_bytes(), self.test_file_data)

    def test_create_complete_in_progress(self) -> None:
        """
        Test that a file is still marked as being copied when its size is less
        than expected.
        """
        self.handler.working_files[self.test_file] = \
            len(self.test_file_data) - 1
        self.handler.create_complete(
            FileSystemEvents.MODIFIED.value, self.source, self.test_file,
            self.dest, self.patch_path)

        self.assertIn(self.test_file, self.handler.working_files)

    @patch('syncdog.base_handler.BaseHandler.track_work_file')
    @patch('shutil.copy2')
    def test_create_complete_permission_error(
            self,
            mock_shutil_copy2: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that a PermissionError is handled correctly when copying a file.
        """
        self.handler.working_files[self.test_file] = len(self.test_file_data)
        mock_shutil_copy2.side_effect = PermissionError

        self.handler.create_complete(
            FileSystemEvents.CREATED.value, self.source, self.test_file,
            self.dest, self.patch_path)
        mock_track_work_file.assert_called_once_with(
            FileSystemEvents.CREATED.value, self.source, self.test_file,
            self.dest, self.patch_path)

    def test_create_directory(self) -> None:
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

        self.handler.create_directory(self.source, source_dir, self.dest)
        time.sleep(1)
        dest_dir = self.dest / source_dir.name
        self.assertTrue(dest_dir.exists())

    def test_create_file_missing_parent_dir(self) -> None:
        """
        Test the create_file method when the parent directory of the destination
        file does not exist.
        """
        test_dir = self.source / "test_dir"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file_2 = test_dir / "test_file.txt"
        with test_file_2.open('wb') as file:
            file.write(b'Hello, World!')

        self.handler.create_file(self.source, test_file_2, self.dest)

        self.assertTrue((self.dest / 'test_dir' / test_file_2).exists())

    @patch('shutil.copy2')
    def test_create_file_permission_error(self, mock_copy2: MagicMock) -> None:
        """
        Test the create_file method when the source file has permission issues.
        """
        mock_copy2.side_effect = PermissionError

        with self.assertRaises(PermissionError):
            self.handler.create_file(self.source, self.test_file, self.dest)

    def test_delete_file(self) -> None:
        """
        Test the delete_file method to ensure it deletes the specified file from
        the destination directory.
        """
        src_file = self.source / self.test_file
        dest_file = self.dest / "test_file.txt"
        dest_file.touch()
        self.assertTrue(dest_file.exists())

        self.handler.delete(self.source, src_file, self.dest)

        self.assertFalse(dest_file.exists())

    def test_delete_directory(self) -> None:
        """
        Test the deletion of a directory.
        This test verifies that a directory is properly deleted by the handler.
        """
        temp_dir = "test_dir"
        src_dir = self.source / temp_dir
        dest_dir = self.dest / temp_dir
        dest_dir.mkdir()
        self.assertTrue(dest_dir.exists())

        self.handler.delete(self.source, src_dir, self.dest)

        self.assertFalse(dest_dir.exists())

    @patch('pathlib.Path.unlink')
    @patch('shutil.rmtree')
    def test_delete_file_not_exists(
            self,
            mock_unlink: MagicMock,
            mock_rmtree: MagicMock,
    ) -> None:
        source_path = self.source / "non_existent_dir"
        source_path.mkdir()
        self.handler.delete(self.source, source_path, self.dest)

        mock_rmtree.assert_not_called()
        mock_unlink.assert_not_called()

    def test_get_dest_path(self) -> None:
        dest_path = self.handler.get_dest_path(
            self.source, self.test_file, self.dest)
        self.assertEqual(dest_path, self.dest / self.test_file.name)

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
        dest_file = self.dest / "test_file.txt"
        # Create the source and destination files
        dest_file.touch()
        self.assertTrue(dest_file.exists())

        new_dest_file = self.dest / "new_name.txt"

        # Simulate the rename event
        event = FileSystemEvent(src_path=str(self.test_file),
                                dest_path=str(self.source / "new_name.txt"))
        event.event_type = FileSystemEvents.MOVED.value

        self.handler.rename(event, self.source, self.dest)

        # Check that the old file no longer exists and the new file exists
        self.assertFalse(dest_file.exists())
        self.assertTrue(new_dest_file.exists())

    @patch('shutil.move')
    def test_rename_dest_path_exists(self, mock_move: MagicMock) -> None:
        """
        Test the rename method when the destination path already exists.
        """
        dest_file = self.dest / "test_file.txt"
        new_dest_file = self.dest / "new_name.txt"
        new_dest_file.touch()

        event = FileSystemEvent(src_path=str(self.test_file),
                                dest_path=str(self.source / "new_name.txt"))
        event.event_type = FileSystemEvents.MOVED.value

        self.handler.rename(event, self.source, self.dest)

        self.assertFalse(dest_file.exists())
        self.assertTrue(new_dest_file.exists())
        mock_move.assert_not_called()

    def test_set_debounce_interval(self) -> None:
        """
        Test the set_debounce_interval method to ensure it correctly sets the
        debounce interval.
        """
        self.assertEqual(self.handler.debounce_interval, 0.5)

        self.handler.set_debounce_interval(50.0)
        self.assertEqual(self.handler.debounce_interval, 50.0)

        self.handler.set_debounce_interval(0.0)
        self.assertEqual(self.handler.debounce_interval, 0.0)

    @patch('threading.Timer')
    def test_start_working_timer(self, mock_timer: MagicMock) -> None:
        """
        Test the start_working_timer method to ensure it correctly starts a
        timer for the given file system event and source path.
        """
        event_type = FileSystemEvents.CREATED.value
        self.handler.working_timers = {}

        existing_timer = MagicMock()
        self.handler.working_timers[self.test_file] = existing_timer

        self.handler.start_working_timer(
            event_type, self.source, self.test_file, self.dest,
            self.patch_path)

        mock_timer.assert_called_once_with(
            self.handler.debounce_interval,
            self.handler.create_complete,
            [event_type, self.source, self.test_file, self.dest,
             self.patch_path])
        self.assertIn(self.test_file, self.handler.working_timers)
        mock_timer.return_value.start.assert_called_once()

    def test_sync_file_success(self) -> None:
        """
        Test the sync_file method for successfully syncing a file.
        """
        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)
        time.sleep(1)

        dest_file = self.dest / self.test_file.relative_to(self.source)
        self.assertTrue(dest_file.exists())
        self.assertEqual(dest_file.read_bytes(), self.test_file_data)

    def test_sync_file_not_exists(self) -> None:
        """
        Test the sync_file method for a source file that does not exist.
        """
        src_file = self.source / "non_existent_file.txt"
        self.handler.sync_file(self.source, src_file,
                               self.dest, self.patch_path)

        dest_file = self.dest / src_file.relative_to(self.source)
        self.assertFalse(dest_file.exists())

    def test_sync_file_source_is_dir(self) -> None:
        """
        Test the sync_file method for a source path that is a directory.
        """
        src_dir = self.source / "test_dir"
        src_dir.mkdir(parents=True, exist_ok=True)

        self.handler.sync_file(self.source, src_dir,
                               self.dest, self.patch_path)

        dest_dir = self.dest / src_dir.relative_to(self.source)
        self.assertTrue(dest_dir.exists())

    def test_sync_file_creates_directory(self) -> None:
        """
        Test the sync_file method for creating a directory if the source path is
        a directory.
        """
        src_dir = self.source / "test_dir"
        src_dir.mkdir(parents=True, exist_ok=True)

        self.handler.sync_file(self.source, src_dir,
                               self.dest, self.patch_path)

        self.assertTrue(
            (self.dest / src_dir.relative_to(self.source)).exists())

    @patch('bsdiff4.file_diff')
    @patch('bsdiff4.file_patch')
    def test_sync_file_creates_patch(
            self,
            mock_file_diff: MagicMock,
            mock_file_patch: MagicMock
    ) -> None:
        """
        Test the sync_file method for creating a patch when the destination
        file exists.
        """
        dest_file = self.dest / self.test_file.relative_to(self.source)
        with dest_file.open('wb') as f:
            f.write(b"Old content")

        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)
        mock_file_diff.assert_called_once()
        mock_file_patch.assert_called_once()

    @patch('pathlib.Path.unlink')
    def test_sync_file_removes_larger_dest_file(
            self,
            mock_unlink: MagicMock
    ) -> None:
        """
        Test the sync_file method for removing the destination file if it is
        larger than the source file.
        """
        dest_file = self.dest / self.test_file.relative_to(self.source)
        patch_file = self.patch_path / \
            self.test_file.relative_to(self.source).with_suffix('.patch')
        patch_file.touch()
        with dest_file.open('wb') as f:
            f.write(b"Hello, World! Hello, World!")

        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)
        mock_unlink.assert_has_calls([call(), call()])

    @patch('syncdog.base_handler.BaseHandler.start_working_timer')
    def test_sync_file_patch_path_not_exists(
            self,
            mock_start_working_timer: MagicMock
    ) -> None:
        """
        Test the sync_file method when the patch path does not exist.
        """
        self.dest_file = self.dest / self.test_file.relative_to(self.source)
        shutil.copy2(self.test_file, self.dest)
        with open(self.test_file, 'wb') as file:
            file.write(b'Hello, World!')

        self.patch_path.rmdir()
        self.assertTrue(self.dest_file.exists())
        self.assertFalse(self.patch_path.exists())

        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)

        self.assertTrue(self.patch_path.exists())
        mock_start_working_timer.assert_called_once_with(
            'modified', self.source, self.test_file, self.dest, self.patch_path
        )

    @patch('syncdog.base_handler.BaseHandler.track_work_file')
    def test_sync_file_ioerror(self, mock_track_work_file: MagicMock) -> None:
        """
        Test the sync_file method for handling IOError.
        """
        mock_track_work_file.side_effect = IOError("Test IOError")

        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)

        mock_track_work_file.assert_called_once_with(
            FileSystemEvents.CREATED.value, self.source, self.test_file,
            self.dest, self.patch_path
        )

    @patch('syncdog.base_handler.BaseHandler.start_working_timer')
    @patch('syncdog.base_handler.BaseHandler.track_work_file')
    def test_sync_file_permissionerror(
            self,
            mock_track_work_file: MagicMock,
            mock_start_working_timer: MagicMock
    ) -> None:
        """
        Test the sync_file method for handling PermissionError.
        """
        mock_track_work_file.side_effect = \
            PermissionError("Test PermissionError")

        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)

        mock_track_work_file.assert_called_once_with(
            'created', self.source, self.test_file, self.dest, self.patch_path)
        mock_start_working_timer.assert_called_once_with(
            'modified', self.source, self.test_file, self.dest,
            self.patch_path
        )

    @patch('syncdog.base_handler.BaseHandler.track_work_file')
    @patch('syncdog.base_handler.Logger.error')
    def test_sync_file_logs_error(
            self,
            mock_logger_error: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test the sync_file method for logging an error if an exception occurs.
        """
        mock_track_work_file.side_effect = Exception("Test exception")
        self.handler.sync_file(self.source, self.test_file,
                               self.dest, self.patch_path)

        mock_logger_error.assert_called_once_with(
            "Error syncing file: Test exception")

    def test_track_work_file_not_exists(self) -> None:
        """
        Test the track_work_file method when the source file does not exist.
        """
        src_file = self.source / "non_existent_file.txt"
        self.handler.track_work_file(
            FileSystemEvents.CREATED.value, self.source, src_file,
            self.dest, self.patch_path)
        self.assertNotIn(src_file, self.handler.working_files)


if __name__ == '__main__':
    unittest.main()
