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

    def test_toggle_buttons_enabled_enabled(self) -> None:
        """
        Test that the toggle_buttons_enabled method enables the action and refresh
        buttons.
        """
        self.window.toggle_buttons_enabled(True)
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    def test_toggle_buttons_enabled_not_enabled(self) -> None:
        """
        Test that the toggle_buttons_enabled method disables the action and refresh buttons.
        """

        self.window.toggle_buttons_enabled(False)
        self.assertFalse(self.window.button_action.isEnabled())
        self.assertFalse(self.window.button_refresh.isEnabled())

    def test_toggle_buttons_enabled_enabled_start_action_true(self) -> None:
        """
        Test that all buttons are enabled when toggle_buttons_enabled is called with True.
        """
        self.window.toggle_buttons_enabled(True)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())

    def test_toggle_buttons_enabled_not_enabled_start_action_true(self) -> None:
        """
        Test that the 'toggle_buttons_enabled' method enables all relevant buttons when
        the start action is set to True.

        This test verifies that when the 'toggle_buttons_enabled' method is called with a
        False argument, the following buttons are disabled:
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
