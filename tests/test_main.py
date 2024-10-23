import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from syncdog.constants import SyncMode
import main


class TestMain(unittest.TestCase):
    @patch('main.threading.Thread')
    @patch('main.handler')
    @patch('main.observer')
    def test_start_syncing_atob(
        self,
        mock_observer: MagicMock,
        mock_file_handler: MagicMock,
        mock_thread: MagicMock
    ) -> None:
        source = Path(r'C:\source')
        destination = Path(r'C:\destination')

        main.start_syncing(SyncMode.ATOB, source, destination)

        mock_file_handler.change_source.assert_called_once_with(source)
        mock_file_handler.change_destination.assert_called_once_with(
            destination)
        mock_observer.change_directory.assert_called_once_with(source)
        mock_thread.assert_called_once_with(target=mock_observer.run)
        mock_thread.return_value.start.assert_called_once()

    @patch('main.threading.Thread')
    @patch('main.handler')
    @patch('main.observer')
    def test_start_syncing_btoa(
        self,
        mock_observer: MagicMock,
        mock_file_handler: MagicMock,
        mock_thread: MagicMock
    ) -> None:
        source = Path(r'C:\source')
        destination = Path(r'C:\destination')

        main.start_syncing(SyncMode.BTOA, source, destination)

        mock_file_handler.change_source.assert_called_once_with(destination)
        mock_file_handler.change_destination.assert_called_once_with(source)
        mock_observer.change_directory.assert_called_once_with(destination)
        mock_thread.assert_called_once_with(target=mock_observer.run)
        mock_thread.return_value.start.assert_called_once()

    # # TODO: Implement this test
    # @patch('main.threading.Thread')
    # @patch('main.handler')
    # @patch('main.observer')
    # def test_start_syncing_mirror(
    #     self,
    #     mock_observer: MagicMock,
    #     mock_file_handler: MagicMock,
    #     mock_thread: MagicMock
    # ) -> None:
    #     source = Path(r'C:\source')
    #     destination = Path(r'C:\destination')

    #     main.start_syncing(SyncMode.MIRROR, source, destination)

    #     mock_file_handler.change_source.assert_called_once_with(source)
    #     mock_file_handler.change_destination.assert_called_once_with(
    #         destination)
    #     mock_observer.change_directory.assert_called_once_with(source)
    #     mock_thread.assert_called_once_with(target=mock_observer.run)
    #     mock_thread.return_value.start.assert_called_once()

    @patch('main.observer')
    @patch('main.handler')
    def test_stop_observer(self, mock_handler, mock_observer) -> None:
        main.stop_observer(mock_observer, mock_handler)

        mock_observer.stop.assert_called_once()
        mock_handler.cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main()
