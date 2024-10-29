from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import main
from syncdog.constants import SyncMode


class TestMain(unittest.TestCase):
    @patch('main.QApplication')
    @patch('main.SyncDogWindow')
    @patch('main.sys')
    def test_main(self, mock_sys, mock_syncdog_window, mock_qapp) -> None:
        mock_window = MagicMock()
        mock_window.show = MagicMock()

        mock_sys.argv = ['main.py']
        mock_syncdog_window.return_value = mock_window
        mock_app_instance = MagicMock()
        mock_qapp.return_value = mock_app_instance

        main.main()

        mock_qapp.assert_called_once_with(mock_sys.argv)
        mock_syncdog_window.assert_called_once()
        mock_window.start_observer_signal.connect.assert_called_once_with(
            main.start_syncing)
        mock_window.stop_observer_signal.connect.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app_instance.exec.assert_called_once()

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

        mock_file_handler.set_source.assert_called_once_with(source)
        mock_file_handler.set_destination.assert_called_once_with(
            destination)
        mock_observer.set_directory.assert_called_once_with(source)
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

        mock_file_handler.set_source.assert_called_once_with(source)
        mock_file_handler.set_destination.assert_called_once_with(destination)
        mock_observer.set_directory.assert_called_once_with(source)
        mock_thread.assert_called_once_with(target=mock_observer.run)
        mock_thread.return_value.start.assert_called_once()

    @patch('main.threading.Thread')
    @patch('main.mirror_handler')
    @patch('main.observer')
    def test_start_syncing_mirror(
        self,
        mock_observer: MagicMock,
        mock_mirror_handler: MagicMock,
        mock_thread: MagicMock
    ) -> None:
        source = Path(r'C:\source')
        destination = Path(r'C:\destination')

        main.start_syncing(SyncMode.MIRROR, source, destination)

        mock_mirror_handler.set_dir_a.assert_called_once_with(source)
        mock_mirror_handler.set_dir_b.assert_called_once_with(
            destination)
        mock_observer.set_directory.assert_called_once_with(
            [source, destination])
        mock_thread.assert_called_once_with(target=mock_observer.run)
        mock_thread.return_value.start.assert_called_once()

    @patch('main.observer')
    @patch('main.handler')
    @patch('main.mirror_handler')
    def test_stop_observer(
            self,
            mock_mirror_handler: MagicMock,
            mock_handler: MagicMock,
            mock_observer: MagicMock
    ) -> None:
        main.stop_observer()

        mock_observer.stop.assert_called_once()
        mock_handler.cleanup.assert_called_once()
        mock_mirror_handler.cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main()
