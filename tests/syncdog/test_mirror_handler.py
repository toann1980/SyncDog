import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from logger import Logger

from syncdog.mirror_handler import MirrorHandler
from syncdog.constants import FileSystemEvents
from watchdog.events import FileSystemEvent


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class TestMirrorHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.dir_a = Path(self.temp_dir) / "dir_a"
        self.dir_b = Path(self.temp_dir) / "dir_b"
        self.dir_b.mkdir()
        self.dir_a.mkdir()
        self.handler = MirrorHandler(dir_a=self.dir_a, dir_b=self.dir_b)
        self.patch_path_a = self.handler.patch_path_a
        self.patch_path_b = self.handler.patch_path_b

        self.test_file_a = self.dir_a / "test_file.txt"
        self.test_file_data = b"Hello, World!"
        with self.test_file_a.open('wb') as f:
            f.write(self.test_file_data)

        self.test_file_b = self.dir_b / "test_file.txt"
        with self.test_file_b.open('wb') as f:
            f.write(self.test_file_data)

    @patch('syncdog.mirror_handler.MirrorHandler.create_directory')
    @patch('syncdog.mirror_handler.MirrorHandler.delete')
    @patch('syncdog.mirror_handler.MirrorHandler.get_directories')
    @patch('syncdog.mirror_handler.MirrorHandler.rename')
    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_dir_a_none(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_get_directories: MagicMock,
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
        self.handler.dir_a = None
        event = FileSystemEvent(src_path=str(self.test_file_a))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)
        mock_create_directory.assert_not_called()
        mock_delete.assert_not_called()
        mock_get_directories.assert_not_called()
        mock_rename.assert_not_called()
        mock_track_work_file.assert_not_called()

    @patch('syncdog.mirror_handler.MirrorHandler.create_directory')
    @patch('syncdog.mirror_handler.MirrorHandler.get_directories')
    @patch('syncdog.mirror_handler.MirrorHandler.delete')
    @patch('syncdog.mirror_handler.MirrorHandler.rename')
    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_dir_b_none(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_get_directories: MagicMock,
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
        self.handler.dir_b = None
        event = FileSystemEvent(src_path=str(self.test_file_b))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)
        mock_create_directory.assert_not_called()
        mock_get_directories.assert_not_called()
        mock_delete.assert_not_called()
        mock_rename.assert_not_called()
        mock_track_work_file.assert_not_called()

    @patch('syncdog.mirror_handler.MirrorHandler.create_directory')
    @patch('syncdog.mirror_handler.MirrorHandler.delete')
    @patch('syncdog.mirror_handler.MirrorHandler.get_directories')
    @patch('syncdog.mirror_handler.MirrorHandler.rename')
    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_syncdog_in_path(
            self,
            mock_create_directory: MagicMock,
            mock_delete: MagicMock,
            mock_get_directories: MagicMock,
            mock_rename: MagicMock,
            mock_track_work_file: MagicMock
    ) -> None:
        event_path = self.dir_a / ".syncdog" / "created_file.txt"
        event = FileSystemEvent(src_path=str(event_path))
        event.event_type = FileSystemEvents.CREATED.value

        self.handler.on_any_event(event)

        mock_create_directory.assert_not_called()
        mock_delete.assert_not_called()
        mock_get_directories.assert_not_called()
        mock_rename.assert_not_called()
        mock_track_work_file.assert_not_called()

    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_created_file(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Verifies that the `track_work_file` method is called exactly once with
        the correct event type and file path.
        """
        event = FileSystemEvent(src_path=str(self.test_file_a))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = False

        self.handler.on_any_event(event)
        mock_track_work_file.assert_called_once_with(
            event.event_type, self.dir_a, self.test_file_a, self.dir_b,
            self.patch_path_b)

    @patch('syncdog.mirror_handler.MirrorHandler.create_directory')
    def test_on_any_event_created_directory(
            self,
            mock_create_directory: MagicMock
    ) -> None:
        """
        Test the `on_any_event` method for handling a created directory event.
        """
        new_dir = self.dir_a / "new_dir"
        event = FileSystemEvent(src_path=str(new_dir))
        event.event_type = FileSystemEvents.CREATED.value
        event.is_directory = True

        self.handler.on_any_event(event)
        mock_create_directory.assert_called_once_with(
            self.dir_a, new_dir, self.dir_b)

    @patch('syncdog.mirror_handler.MirrorHandler.delete')
    def test_on_any_event_deleted_file(self, mock_delete: MagicMock) -> None:
        """
        Test the handler's response to a file deletion event.
        This test simulates a file deletion event and verifies that the
        handler's `delete` method is called exactly once with the correct file
        path.
        """
        self.assertTrue(self.test_file_a.exists())
        event = FileSystemEvent(src_path=str(self.test_file_a))
        event.event_type = FileSystemEvents.DELETED.value

        self.handler.on_any_event(event)
        mock_delete.assert_called_once_with(
            self.dir_a, self.test_file_a, self.dir_b)

    @patch('syncdog.mirror_handler.MirrorHandler.rename')
    def test_on_any_event_moved_file(self, mock_rename: MagicMock) -> None:
        """
        This test verifies that the `rename` method is called once with the
        correct event when a file is moved.
        """
        test_file_moved = self.dir_a / "moved_file.txt"
        self.assertFalse(test_file_moved.exists())

        event = FileSystemEvent(
            src_path=str(self.test_file_a), dest_path=str(test_file_moved))
        event.event_type = FileSystemEvents.MOVED.value
        self.handler.on_any_event(event)

        mock_rename.assert_called_once_with(
            event, self.dir_a, self.dir_b)

    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_modified_file(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler correctly tracks a modified file event.
        """
        with open(self.test_file_a, 'ab') as file:
            file.write(b"Hallo, World!")
        event = FileSystemEvent(src_path=str(self.test_file_a))
        event.event_type = FileSystemEvents.MODIFIED.value

        self.handler.on_any_event(event)

        mock_track_work_file.assert_called_once_with(
            event.event_type, self.dir_a, self.test_file_a, self.dir_b,
            self.patch_path_b)
        self.assertEqual(
            self.handler.working_files[self.test_file_b],
            self.test_file_b.stat().st_size)

    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_modified_is_directory(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler does not track a modified directory event.
        """
        modified_dir = self.dir_a / "modified_dir"
        modified_dir.mkdir()
        event = FileSystemEvent(src_path=str(modified_dir))
        event.event_type = FileSystemEvents.MODIFIED.value
        event.is_directory = True

        self.handler.on_any_event(event)
        self.assertNotIn(modified_dir, self.handler.working_files)
        mock_track_work_file.assert_not_called()

    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_modified_file_in_working_files(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler does not track a file copy event when the file is
        being copied.
        """
        modified_file = self.dir_a / "modified_file.txt"
        event = FileSystemEvent(src_path=str(modified_file))
        event.event_type = FileSystemEvents.MODIFIED.value

        self.handler.working_files[Path(event.src_path)] = \
            len(self.test_file_data)

        self.handler.on_any_event(event)
        mock_track_work_file.assert_not_called()

    @patch('syncdog.mirror_handler.MirrorHandler.track_work_file')
    def test_on_any_event_dest_path_exists(
            self,
            mock_track_work_file: MagicMock
    ) -> None:
        """
        Test that the handler does not track a modified file event when the
        destination file already exists.
        """
        event = FileSystemEvent(src_path=str(self.test_file_a))
        event.event_type = FileSystemEvents.MODIFIED.value

        self.handler.on_any_event(event)

        mock_track_work_file.assert_not_called()

    def test_cleanup(self) -> None:
        """
        Test the `cleanup` method.
        """
        self.handler.cleanup()
        self.assertFalse(self.patch_path_a.exists())
        self.assertFalse(self.patch_path_b.exists())
        self.assertIsNone(self.handler.patch_path_a)
        self.assertIsNone(self.handler.patch_path_b)

    def test_get_directories(self) -> None:
        """
        Test the `get_directories` method.
        """
        dir_a, patch_path = self.handler.get_directories(self.test_file_a)
        self.assertEqual(self.handler.dir_a, dir_a)
        self.assertEqual(self.handler.patch_path_b, patch_path)

        dir_b, patch_path = self.handler.get_directories(self.test_file_b)
        self.assertEqual(self.handler.dir_b, dir_b)
        self.assertEqual(self.handler.patch_path_a, patch_path)

    def test_get_directories_dir_a(self) -> None:
        """
        Test the `get_directories` method when the directories are not set.
        """
        self.handler.dir_a = None

        with self.assertRaises(ValueError):
            self.handler.get_directories(self.test_file_a)

    def test_get_directories_dir_b(self) -> None:
        """
        Test the `get_directories` method when the directories are not set.
        """
        self.handler.dir_b = None

        with self.assertRaises(ValueError):
            self.handler.get_directories(self.test_file_b)

    def test_set_dir_a(self) -> None:
        """
        Test the `set_dir_a` method.
        """
        self.handler.set_dir_a(self.dir_a)
        self.assertEqual(self.handler.dir_a, self.dir_a)
        self.assertEqual(self.handler.patch_path_b, self.patch_path_b)

    def test_set_dir_b(self) -> None:
        """
        Test the `set_dir_b` method.
        """
        self.handler.set_dir_b(self.dir_b)
        self.assertEqual(self.handler.dir_b, self.dir_b)
        self.assertEqual(self.handler.patch_path_a, self.patch_path_a)
