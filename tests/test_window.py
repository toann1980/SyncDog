import os
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from PySide6 import QtTest, QtCore, QtWidgets
from syncdog.window import SyncDogWindow
from syncdog.constants import SyncMode
from typing import Literal


class TestSyncFilesWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not QtWidgets.QApplication.instance():
            cls.app = QtWidgets.QApplication([])

    def setUp(self) -> None:
        os.environ['UNIT_TESTING'] = '1'
        self.window = SyncDogWindow()
        self.window.show()

    def test_initial_state(self) -> None:
        """Check initial state of the window"""
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.windowTitle(), 'SyncDog')

        self.assertEqual(self.window.mode, SyncMode.IDLE)

    def test_initial_state_buttons(self) -> None:
        """Initial state of buttons"""
        for button in (
            {'name': 'button_a', 'enabled': True, 'text': '...'},
            {'name': 'button_b', 'enabled': True, 'text': '...'},
            {'name': 'button_AtoB', 'enabled': True, 'text': 'A to B'},
            {'name': 'button_BtoA', 'enabled': True, 'text': 'B to A'},
            {'name': 'button_mirror', 'enabled': True, 'text': 'Mirror'},
            {'name': 'button_action', 'enabled': False, 'text': 'Synchronize'},
            {'name': 'button_refresh', 'enabled': False, 'text': 'Refresh'}
        ):
            current_button = self.window.findChild(
                QtWidgets.QPushButton, button['name'])
            self.assertIsNotNone(current_button)
            self.assertTrue(current_button.isEnabled() == button['enabled'])
            self.assertEqual(current_button.text(), button['text'])

    def test_initial_tray(self) -> None:
        """
        Verifies the tray icon is not None and is visible.
        """
        tray_icon = self.window.findChild(
            QtWidgets.QSystemTrayIcon, 'tray_icon')
        self.assertIsNotNone(tray_icon)
        self.assertEqual(tray_icon.isVisible(), True)
        # self.assertEqual()

    def test_tray_icon_action(self) -> None:
        """
        Test the tray icon action to ensure that double-clicking the tray icon
        makes the window visible and active.
        """
        self.window.hide()
        self.assertFalse(self.window.isVisible())
        self.assertFalse(self.window.isActiveWindow())
        tray_icon = self.window.findChild(
            QtWidgets.QSystemTrayIcon, 'tray_icon')
        self.assertIsNotNone(tray_icon)

        tray_icon.activated.emit(QtWidgets.QSystemTrayIcon.DoubleClick)

        QtTest.QTest.qWait(100)

        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.isActiveWindow())

    def test_intiial_state_statusbar(self) -> None:
        """
        Ensures that the status bar is present and its initial message is empty.
        """
        statusbar = self.window.findChild(
            QtWidgets.QStatusBar, 'statusbar')
        self.assertIsNotNone(statusbar)
        self.assertEqual(statusbar.currentMessage(), '')

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_alpha(
        self,
        mock_get_existing_directory: MagicMock
    ) -> None:
        """
        Test the button action for setting the alpha path.

        Args:
            mock_get_existing_directory (MagicMock): Mock for the directory
                selection dialog.
        """
        mock_get_existing_directory.return_value = r"C:\source_a"

        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_a.text(), r"C:\source_a")
        self.assertEqual(self.window.alpha_path, Path(r"C:\source_a"))

    @patch('syncdog.window.SyncDogWindow.select_path')
    def test_button_path_action_alpha_gui_testing(
        self,
        mock_select_path: MagicMock
    ) -> None:
        """
        Test the button action for setting the alpha path when GUI_TESTING is
        set.
        """

        os.environ['GUI_TESTING'] = '1'
        mock_select_path.return_value = r'C:\tmp\SyncDogTest'

        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        mock_select_path.assert_called_once_with(
            caption='Select Directory A', dir=r'C:\tmp\SyncDogTest'
        )
        self.assertEqual(self.window.label_a.text(), r'C:\tmp\SyncDogTest')
        self.assertEqual(self.window.alpha_path, Path(r'C:\tmp\SyncDogTest'))

    @patch('syncdog.window.SyncDogWindow.select_path')
    def test_button_path_action_beta_gui_testing(
        self,
        mock_select_path: MagicMock
    ) -> None:
        """
        Test the button action for setting the alpha path when GUI_TESTING is
        set.
        """

        os.environ['GUI_TESTING'] = '1'
        mock_select_path.return_value = r'C:\tmp\SyncDogTest_Dest'

        button = self.window.findChild(QtWidgets.QPushButton, 'button_b')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        mock_select_path.assert_called_once_with(
            caption='Select Directory B', dir=r'C:\tmp\SyncDogTest_Dest'
        )
        self.assertEqual(
            self.window.label_b.text(), r'C:\tmp\SyncDogTest_Dest')
        self.assertEqual(
            self.window.beta_path, Path(r'C:\tmp\SyncDogTest_Dest'))

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_beta(
        self,
        mock_get_existing_directory: MagicMock
    ) -> None:
        """
        Test the button action for setting the beta path.

        Args:
            mock_get_existing_directory (MagicMock): Mock for the directory
                selection dialog.
        """

        mock_get_existing_directory.return_value = r"C:\source_b"

        button = self.window.findChild(QtWidgets.QPushButton, 'button_b')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_b.text(), r"C:\source_b")
        self.assertEqual(self.window.beta_path, Path(r"C:\source_b"))

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_empty(
        self,
        mock_get_existing_directory: MagicMock
    ) -> None:
        """
        Test case for verifying the behavior when the directory selection button
        is clicked but no directory is selected.
        Args:
            mock_get_existing_directory (MagicMock): Mock object for the
                directory selection dialog.
        """
        mock_get_existing_directory.return_value = ''
        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_a.text(), 'Select a directory...')
        self.assertEqual(self.window.alpha_path, None)

    def test_button_click_a_to_b(self) -> None:
        """
        Test the button click event that changes the mode from A to B.
        """
        button = self.window.findChild(QtWidgets.QPushButton, 'button_AtoB')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.ATOB)

    def test_button_click_b_to_a(self) -> None:
        """
        Test the button click event that changes the mode from B to A.
        """
        button = self.window.findChild(QtWidgets.QPushButton, 'button_BtoA')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.BTOA)

    def close_active_widget(self, button: Literal['yes', 'no'] = 'no') -> None:
        """
        Closes the active widget by simulating a button click on a confirmation
        message box.
        Args:
            button (Literal['yes', 'no']): The button to click on the message
                box. Defaults to 'no'.
        """

        message_box = self.window.findChild(
            QtWidgets.QMessageBox, 'confirmQuitMessageBox')
        QtTest.QTest.qWaitForWindowExposed(message_box)
        self.assertIsNotNone(message_box)

        press = message_box.button(QtWidgets.QMessageBox.No) if button == 'no' \
            else message_box.button(QtWidgets.QMessageBox.Yes)
        self.assertIsNotNone(press)
        self.assertTrue(press.isVisible())
        # Simulate a left mouse click on the "No" button
        QtTest.QTest.mouseClick(press, QtCore.Qt.LeftButton)
        if button == 'no':
            self.assertTrue(self.window.isVisible())

    def test_close_event_yes_button(self) -> None:
        """
        Test the close event of the window when the 'yes' button is clicked.
        """

        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())
        QtCore.QTimer.singleShot(250, lambda: self.close_active_widget('yes'))
        self.window.close()

        os.environ['UNIT_TESTING'] = '1'

    def test_close_event_no_button(self) -> None:
        """
        Test the close event of the window when the 'no' button is clicked.
        """

        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())
        QtCore.QTimer.singleShot(250, lambda: self.close_active_widget('no'))

        self.window.close()
        os.environ['UNIT_TESTING'] = '1'

    @patch('PySide6.QtWidgets.QMessageBox.exec',
           return_value=QtWidgets.QMessageBox.Ok)
    def test_confirm_start_ok(self, mock_exec: MagicMock) -> None:
        """Test confirm_start method when 'OK' is clicked."""
        result = self.window.confirm_start()
        self.assertTrue(result)
        mock_exec.assert_called_once()

    @patch('PySide6.QtWidgets.QMessageBox.exec',
           return_value=QtWidgets.QMessageBox.Cancel)
    def test_confirm_start_cancel(self, mock_exec: MagicMock) -> None:
        """Test confirm_start method when 'Cancel' is clicked."""
        result = self.window.confirm_start()
        self.assertFalse(result)
        mock_exec.assert_called_once()

    def test_main_button_stop_action(self) -> None:
        """
        Test the main button stop action in the SyncDogWindow. Verifies when the
        main button is set to 'Stop', the button text changes to 'Synchronize',
        the stop signal is emitted once, the start signal is not emitted, and
        the toggle_buttons_enabled method is called with the correct parameters.
        """
        self.window.alpha_path = Path(r'C:\source')
        self.window.alpha_path = Path(r'C:\dest')
        self.window.mode = SyncMode.ATOB
        self.window.button_a.setEnabled(False)
        self.window.button_b.setEnabled(False)
        self.window.button_AtoB.setEnabled(False)
        self.window.button_BtoA.setEnabled(False)
        self.window.button_mirror.setEnabled(False)
        self.window.button_refresh.setEnabled(False)
        self.window.button_action.setEnabled(True)
        self.window.button_action.setText('Stop')
        spy_stop = QtTest.QSignalSpy(self.window.stop_observer_signal)
        spy_start = QtTest.QSignalSpy(self.window.start_observer_signal)

        self.window.main_button_action()

        self.assertEqual(self.window.button_action.text(), "Synchronize")
        self.assertEqual(spy_stop.count(), 1)
        self.assertEqual(spy_start.count(), 0)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    def test_main_button_action(self) -> None:
        """
        Test the main_button_action method when the observer is started.
        """
        self.window.alpha_path = Path(r'C:\source')
        self.window.beta_path = Path(r'C:\dest')
        self.window.mode = SyncMode.ATOB
        self.window.button_a.setEnabled(True)
        self.window.button_b.setEnabled(True)
        self.window.button_AtoB.setEnabled(True)
        self.window.button_BtoA.setEnabled(True)
        self.window.button_mirror.setEnabled(True)
        self.window.button_refresh.setEnabled(False)
        self.window.button_action.setEnabled(True)
        spy_stop = QtTest.QSignalSpy(self.window.stop_observer_signal)
        spy_start = QtTest.QSignalSpy(self.window.start_observer_signal)

        self.window.confirm_start = MagicMock(return_value=True)
        self.window.main_button_action()

        self.assertEqual(self.window.button_action.text(), "Stop")
        self.assertEqual(spy_stop.count(), 0)
        self.assertEqual(spy_start.count(), 1)
        self.assertFalse(self.window.button_a.isEnabled())
        self.assertFalse(self.window.button_b.isEnabled())
        self.assertFalse(self.window.button_AtoB.isEnabled())
        self.assertFalse(self.window.button_BtoA.isEnabled())
        self.assertFalse(self.window.button_mirror.isEnabled())
        self.assertTrue(self.window.button_action.isEnabled())

    def test_main_button_action_state_not_ready(self) -> None:
        """
        Test the main_button_action method when state not ready.
        """
        self.window.alpha_path = None
        self.window.beta_path = None
        self.window.mode = SyncMode.ATOB
        self.window.button_a.setEnabled(True)
        self.window.button_b.setEnabled(True)
        self.window.button_AtoB.setEnabled(True)
        self.window.button_BtoA.setEnabled(True)
        self.window.button_mirror.setEnabled(True)
        self.window.button_refresh.setEnabled(True)
        self.window.button_action.setEnabled(True)
        spy_stop = QtTest.QSignalSpy(self.window.stop_observer_signal)
        spy_start = QtTest.QSignalSpy(self.window.start_observer_signal)

        self.window.main_button_action()

        self.assertEqual(self.window.button_action.text(), "Synchronize")
        self.assertEqual(spy_stop.count(), 0)
        self.assertEqual(spy_start.count(), 0)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    def test_main_button_action_state_ready_confirm_false(self) -> None:
        """
        Test the main_button_action method when the observer is not started.
        """
        self.window.alpha_path = Path(r'C:\source')
        self.window.beta_path = Path(r'C:\dest')
        self.window.mode = SyncMode.ATOB
        self.window.button_a.setEnabled(True)
        self.window.button_b.setEnabled(True)
        self.window.button_AtoB.setEnabled(True)
        self.window.button_BtoA.setEnabled(True)
        self.window.button_mirror.setEnabled(True)
        self.window.button_refresh.setEnabled(True)
        self.window.button_action.setEnabled(True)
        spy_stop = QtTest.QSignalSpy(self.window.stop_observer_signal)
        spy_start = QtTest.QSignalSpy(self.window.start_observer_signal)

        self.window.confirm_start = MagicMock(return_value=False)
        self.window.main_button_action()

        self.assertEqual(self.window.button_action.text(), "Synchronize")
        self.assertEqual(spy_stop.count(), 0)
        self.assertEqual(spy_start.count(), 0)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    @patch('syncdog.window.SyncDogWindow.toggle_buttons_enabled')
    def test_mode_switch_atob(
        self,
        mock_toggle_buttons_enabled: MagicMock
    ) -> None:
        self.window.mode_switch("atob")
        self.assertEqual(self.window.mode, SyncMode.ATOB)
        mock_toggle_buttons_enabled.assert_called_once_with(
            enabled=self.window.state_ready())

    @patch('syncdog.window.SyncDogWindow.toggle_buttons_enabled')
    def test_mode_switch_btoa(
        self,
        mock_toggle_buttons_enabled: MagicMock
    ) -> None:
        self.window.mode_switch("btoa")
        self.assertEqual(self.window.mode, SyncMode.BTOA)
        mock_toggle_buttons_enabled.assert_called_once_with(
            enabled=self.window.state_ready())

    @patch('syncdog.window.SyncDogWindow.toggle_buttons_enabled')
    def test_mode_switch_mirror(
        self,
        mock_toggle_buttons_enabled: MagicMock
    ) -> None:
        self.window.mode_switch("mirror")
        self.assertEqual(self.window.mode, SyncMode.MIRROR)
        mock_toggle_buttons_enabled.assert_called_once_with(
            enabled=self.window.state_ready())

    def test_set_directories_atob(self) -> None:
        """Test set_directories method for SyncMode.ATOB."""
        self.window.mode = SyncMode.ATOB
        self.window.alpha_path = Path("/path/to/source")
        self.window.beta_path = Path("/path/to/destination")

        mode, source, destination = self.window.set_directories()

        self.assertEqual(mode, SyncMode.ATOB)
        self.assertEqual(source, Path("/path/to/source"))
        self.assertEqual(destination, Path("/path/to/destination"))

    def test_set_directories_btoa(self) -> None:
        """Test set_directories method for SyncMode.BTOA."""
        self.window.mode = SyncMode.BTOA
        self.window.alpha_path = Path("/path/to/source")
        self.window.beta_path = Path("/path/to/destination")

        mode, source, destination = self.window.set_directories()

        self.assertEqual(mode, SyncMode.BTOA)
        self.assertEqual(source, Path("/path/to/destination"))
        self.assertEqual(destination, Path("/path/to/source"))

    def test_set_directories_mirror(self) -> None:
        """Test set_directories method for SyncMode.MIRROR."""
        self.window.mode = SyncMode.MIRROR
        self.window.alpha_path = Path("/path/to/source")
        self.window.beta_path = Path("/path/to/destination")

        mode, source, destination = self.window.set_directories()

        self.assertEqual(mode, SyncMode.MIRROR)
        self.assertEqual(source, Path("/path/to/source"))
        self.assertEqual(destination, Path("/path/to/destination"))

    @patch('PySide6.QtWidgets.QMessageBox.information')
    def test_state_read_same_paths(self, mock_information: MagicMock) -> None:
        """Test state_ready method when alpha and beta paths are the same."""
        self.window.alpha_path = Path(r'C:\source')
        self.window.beta_path = Path(r'C:\source')
        self.window.mode = SyncMode.ATOB

        mock_information.return_value = QtWidgets.QMessageBox.Ok
        result = self.window.state_ready()

        self.assertFalse(result)
        mock_information.assert_called_once()

    def test_toggle_buttons_enabled_enabled(self) -> None:
        """
        Test that the toggle_buttons_enabled method enables the action and
        refresh buttons.
        """
        self.window.toggle_buttons_enabled(True)
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    def test_toggle_buttons_enabled_not_enabled(self) -> None:
        """
        Test that the toggle_buttons_enabled method disables the action and
        refresh buttons.
        """

        self.window.toggle_buttons_enabled(False)
        self.assertFalse(self.window.button_action.isEnabled())
        self.assertFalse(self.window.button_refresh.isEnabled())

    def test_toggle_buttons_enabled_enabled_start_action_true(self) -> None:
        """
        Test that all buttons are enabled when toggle_buttons_enabled is called
        with True.
        """
        self.window.toggle_buttons_enabled(True)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())

    def test_toggle_buttons_enabled_not_enabled_start_action_true(self) -> None:
        """
        Test that the 'toggle_buttons_enabled' method enables all relevant
        buttons when the start action is set to True.

        This test verifies that when the 'toggle_buttons_enabled' method is
        called with a False argument, the following buttons are disabled:
        button_a, button_b, button_AtoB, button_BtoA, button_mirror
        """
        self.window.toggle_buttons_enabled(enabled=False, start_action=True)
        self.assertFalse(self.window.button_a.isEnabled())
        self.assertFalse(self.window.button_b.isEnabled())
        self.assertFalse(self.window.button_AtoB.isEnabled())
        self.assertFalse(self.window.button_BtoA.isEnabled())
        self.assertFalse(self.window.button_mirror.isEnabled())

    def tearDown(self) -> None:
        self.window.close()

    @classmethod
    def tearDownClass(cls):
        if QtWidgets.QApplication.instance():
            cls.app.quit()
            QtCore.QCoreApplication.quit()


if __name__ == "__main__":
    unittest.main()
