import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from syncdog.file_handler import FileHandler
from syncdog.constants import FileSystemEvents
from watchdog.events import FileSystemEvent


class TestFileHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.source = Path(self.temp_dir) / "source"
        self.dest = Path(self.temp_dir) / "destination"
        self.patch_path = self.dest / '.syncdog'
        self.dest.mkdir()
        self.source.mkdir()
        self.patch_path.mkdir()
        self.handler = FileHandler(
            source=self.source, destination=self.dest)
        self.handler.patch_path = self.patch_path
        self.test_file = self.source / "test_file.txt"
        self.test_file_data = b"Hello, World!"
        with self.test_file.open('wb') as f:
            f.write(self.test_file_data)

    @patch('syncdog.file_handler.FileHandler.create_directory')
    @patch('syncdog.file_handler.FileHandler.delete')
    @patch('syncdog.file_handler.FileHandler.rename')
    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_source_none(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_rename: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test the `on_any_event` method when the source is None.

        This test verifies that when the handler's source is set to None,
        the `on_any_event` method does not call any of the file operation
        methods (`create_directory`, `track_work_file`, `delete`, `rename`)
        regardless of the event type.
        """
        self.handler.source = None
        event = FileSystemEvent(src_path=str(self.source / "created_file.txt"))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)
        mock_track_work_file.assert_not_called()
        mock_create_directory.assert_not_called()
        mock_delete.assert_not_called()
        mock_rename.assert_not_called()

    @patch('syncdog.file_handler.FileHandler.create_directory')
    @patch('syncdog.file_handler.FileHandler.delete')
    @patch('syncdog.file_handler.FileHandler.rename')
    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_destination_none(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_rename: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test the `on_any_event` method when the destination is None.

        This test verifies that when the handler's destination is set to None,
        the `on_any_event` method does not call any of the file operation
        methods (`create_directory`, `track_work_file`, `delete`, `rename`)
        regardless of the event type.
        """
        self.handler.dest = None
        event = FileSystemEvent(src_path=str(self.test_file))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)

        mock_create_directory.assert_not_called()
        mock_delete.assert_not_called()
        mock_rename.assert_not_called()
        mock_track_work_file.assert_not_called()

    @patch('syncdog.file_handler.FileHandler.create_directory')
    @patch('syncdog.file_handler.FileHandler.delete')
    @patch('syncdog.file_handler.FileHandler.rename')
    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_syncdog_in_path(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_rename: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        event_path = self.source / ".syncdog" / "created_file.txt"
        event = FileSystemEvent(src_path=str(event_path))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)

        mock_create_directory.assert_not_called()
        mock_delete.assert_not_called()
        mock_rename.assert_not_called()
        mock_track_work_file.assert_not_called()

    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_created_file(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Verifies that the `track_work_file` method is called exactly once with
        the correct event type and file path.
        """
        event = FileSystemEvent(src_path=str(self.test_file))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = False

        self.handler.on_any_event(event)
        mock_track_work_file.assert_called_once_with(
            event.event_type, self.source, self.test_file, self.dest,
            self.patch_path)

    @patch('syncdog.file_handler.FileHandler.create_directory')
    def test_on_any_event_created_directory(
            self,
            mock_create_directory: MagicMock
    ) -> None:
        """
        Test the `on_any_event` method for handling a created directory event.
        """
        new_dir = self.source / "new_dir"
        event = FileSystemEvent(src_path=str(new_dir))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = True

        self.handler.on_any_event(event)
        mock_create_directory.assert_called_once_with(
            self.source, new_dir, self.dest)

    @patch('syncdog.file_handler.FileHandler.delete')
    def test_on_any_event_deleted_file(self, mock_delete: MagicMock) -> None:
        """
        Test the handler's response to a file deletion event.
        This test simulates a file deletion event and verifies that the
        handler's `delete` method is called exactly once with the correct file
        path.
        """
        self.assertTrue(self.test_file.exists())
        event = FileSystemEvent(src_path=str(self.test_file))
        event.event_type = FileSystemEvents.DELETED.value

        self.handler.on_any_event(event)
        mock_delete.assert_called_once_with(
            self.source, self.test_file, self.dest)

    @patch('syncdog.file_handler.FileHandler.rename')
    def test_on_any_event_moved_file(self, mock_rename: MagicMock) -> None:
        """
        This test verifies that the `rename` method is called once with the
        correct event when a file is moved.
        """
        test_file_moved = self.source / "moved_file.txt"
        self.assertFalse(test_file_moved.exists())

        event = FileSystemEvent(src_path=str(
            self.test_file), dest_path=str(test_file_moved))
        event.event_type = FileSystemEvents.MOVED.value
        self.handler.on_any_event(event)

        mock_rename.assert_called_once_with(
            event, self.source, self.dest)

    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_modified_file(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler correctly tracks a modified file event.
        """
        event = FileSystemEvent(
            src_path=str(self.source / "modified_file.txt")
        )
        event.event_type = FileSystemEvents.MODIFIED.value

        self.handler.on_any_event(event)
        mock_track_work_file.assert_called_once_with(
            event.event_type, self.source, Path(event.src_path), self.dest,
            self.patch_path)

    @patch('syncdog.file_handler.FileHandler.track_work_file')
    def test_on_any_event_modified_file_being_copied(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler does not track a file copy event when the file is
        being copied.
        """

        event = FileSystemEvent(src_path=str(
            self.source / "modified_file.txt"))
        event.event_type = FileSystemEvents.MODIFIED.value

        # Simulate that the file is currently being copied
        self.handler.working_files[Path(event.src_path)] = \
            len(self.test_file_data)

        self.handler.on_any_event(event)
        mock_track_work_file.assert_not_called()

    def test_set_destination(self) -> None:
        """
        Test the set_destination method to ensure it correctly updates the
        handler's destination directory and associated paths.
        """
        new_destination = Path(self.temp_dir) / "new_destination"
        new_destination.mkdir()
        self.handler.set_destination(new_destination)

        self.assertFalse((self.dest / '.syncdog').exists())

        self.assertEqual(self.handler.dest, new_destination)
        self.assertEqual(self.handler.patch_path, new_destination / '.syncdog')
        self.assertTrue((new_destination / '.syncdog').exists())

    def test_set_destination_patch_path_exists(self) -> None:
        """
        Test the set_destination method to ensure it correctly updates the
        destination and patch path, and removes the old patch path.
        """
        new_destination = Path(self.temp_dir) / "new_destination"
        new_destination.mkdir()

        old_patch_path = self.patch_path
        self.handler.set_destination(new_destination)

        self.assertEqual(self.handler.dest, new_destination)
        self.assertEqual(self.handler.patch_path, new_destination / '.syncdog')

        self.assertFalse(old_patch_path.exists())
        self.assertTrue((new_destination / '.syncdog').exists())

    def test_set_source(self) -> None:
        """
        Test the set_source method to ensure it updates the handler's source
        directory.
        """
        new_source = Path(self.temp_dir) / "new_source"
        new_source.mkdir()

        self.handler.set_source(new_source)

        self.assertEqual(self.handler.source, new_source)

    def test_cleanup(self) -> None:
        """
        Test the cleanup method to ensure it removes the patch directory if it
        exists.
        """
        self.handler.cleanup()
        self.assertFalse(self.patch_path.exists())

    def test_repr(self) -> None:
        """
        Test the __repr__ method to ensure it returns the correct string
        """
        self.assertEqual(
            repr(self.handler),
            f'FileHandler(source={self.source}, {self.dest})'
        )

    def test_str(self) -> None:
        """
        Test the __str__ method to ensure it returns the correct string
        """
        self.assertEqual(
            str(self.handler),
            f'FileHandler: Source={
                self.handler.source}, Destination={self.handler.dest}'
        )
