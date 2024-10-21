import os
from pathlib import Path
import unittest
from unittest.mock import patch

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
        Test that the system tray icon is initialized correctly.

        This test verifies that the tray icon is not None and is visible.
        """
        tray_icon = self.window.findChild(
            QtWidgets.QSystemTrayIcon, 'tray_icon')
        self.assertIsNotNone(tray_icon)
        self.assertEqual(tray_icon.isVisible(), True)
        # self.assertEqual()

    def test_tray_icon_action(self) -> None:
        """
        Test the tray icon action for the application window.
        This test verifies that the application window is hidden initially,
        and becomes visible and active when the tray icon is double-clicked.
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
        Test that the status bar is initialized with no message.

        This test verifies that the status bar widget is present in the window
        and that its initial message is an empty string.
        """
        statusbar = self.window.findChild(
            QtWidgets.QStatusBar, 'statusbar')
        self.assertIsNotNone(statusbar)
        self.assertEqual(statusbar.currentMessage(), '')

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_alpha(self, mock_get_existing_directory):
        """
        Test the button path action for 'button_a' in the SyncDog window.
        This test mocks the QFileDialog.getExistingDirectory method to simulate
        a directory selection and verifies that the label and internal path
        are updated correctly when the button is clicked.

        Args:
            mock_get_existing_directory (MagicMock): Mocked method for directory
                selection.
        """
        mock_get_existing_directory.return_value = r"C:\source_a"

        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_a.text(), r"C:\source_a")
        self.assertEqual(self.window.alpha_path, Path(r"C:\source_a"))

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_beta(self, mock_get_existing_directory):
        """
        Test the button path action for 'button_b' in the SyncDog window.
        This test mocks the QFileDialog.getExistingDirectory method to simulate
        a directory selection and verifies that the label and internal path
        are updated correctly when the button is clicked.

        Args:
            mock_get_existing_directory (MagicMock): Mocked method for directory
                selection.
        """
        mock_get_existing_directory.return_value = r"C:\source_b"

        button = self.window.findChild(QtWidgets.QPushButton, 'button_b')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_b.text(), r"C:\source_b")
        self.assertEqual(self.window.beta_path, Path(r"C:\source_b"))

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_empty(self, mock_get_existing_directory):
        """
        Test the behavior when the directory selection button is clicked but no
        directory is selected. 

        This test mocks the directory selection dialog to return an empty
        string, simulates a button click, and verifies that the label text is
        updated to prompt the user to select a directory and that the internal
        path is set to None.
        """

        mock_get_existing_directory.return_value = ''
        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        self.assertEqual(self.window.label_a.text(), 'Select a directory...')
        self.assertEqual(self.window.alpha_path, None)

    def test_button_click_a_to_b(self) -> None:
        """
        Test the button click event that changes the mode from A to B.
        This test simulates a mouse click on the 'button_AtoB' button and 
        verifies that the window's mode is set to SyncMode.ATOB.
        """
        button = self.window.findChild(QtWidgets.QPushButton, 'button_AtoB')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.ATOB)

    def test_button_click_b_to_a(self) -> None:
        """
        Test the button click event that changes the mode from B to A.

        This test simulates a mouse click on the 'button_BtoA' button and
        verifies that the window's mode is set to SyncMode.BTOA.
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
        Returns:
            None
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
        Test the close event when the 'Yes' button is clicked.
        This test verifies that the window is initially visible, simulates a
        'Yes' button click to close the active widget, and ensures the
        environment variable 'UNIT_TESTING' is properly managed before and after
        the test.
        """
        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())
        QtCore.QTimer.singleShot(250, lambda: self.close_active_widget('yes'))
        self.window.close()

        os.environ['UNIT_TESTING'] = '1'

    def test_close_event_no_button(self) -> None:
        """
        Test the close event of the window when no button is pressed.
        This test ensures that the window is visible before attempting to close
        it, and then simulates a close event without pressing any button. It
        verifies that the window's visibility state is correctly handled during
        the close event.
        """
        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())
        QtCore.QTimer.singleShot(250, lambda: self.close_active_widget('no'))

        self.window.close()
        os.environ['UNIT_TESTING'] = '1'

    def test_toggle_ready_enabled(self) -> None:
        """
        Test that the 'toggle_ready' method enables the 'button_action' and
        'button_refresh' buttons.
        """
        self.window.toggle_ready(True)
        self.assertTrue(self.window.button_action.isEnabled())
        self.assertTrue(self.window.button_refresh.isEnabled())

    def test_toggle_ready_not_enabled(self) -> None:
        """
        Test the toggle_ready method when the window is not enabled.

        This test ensures that the toggle_ready method correctly disables the 
        button_action and button_refresh when the window is not enabled.
        """
        self.window.toggle_ready(False)
        self.assertFalse(self.window.button_action.isEnabled())
        self.assertFalse(self.window.button_refresh.isEnabled())

    def test_toggle_ready_enabled_start_action_true(self) -> None:
        """
        Test that the 'toggle_ready' method enables all relevant buttons when
        the start action is set to True.

        This test verifies that when the 'toggle_ready' method is called with a
        True argument, the following buttons are enabled:
        button_a, button_b, button_AtoB, button_BtoA, button_mirror
        """
        self.window.toggle_ready(True)
        self.assertTrue(self.window.button_a.isEnabled())
        self.assertTrue(self.window.button_b.isEnabled())
        self.assertTrue(self.window.button_AtoB.isEnabled())
        self.assertTrue(self.window.button_BtoA.isEnabled())
        self.assertTrue(self.window.button_mirror.isEnabled())

    def test_toggle_ready_not_enabled_start_action_true(self) -> None:
        """
        Test that the 'toggle_ready' method enables all relevant buttons when
        the start action is set to True.

        This test verifies that when the 'toggle_ready' method is called with a
        False argument, the following buttons are disabled:
        button_a, button_b, button_AtoB, button_BtoA, button_mirror
        """
        self.window.toggle_ready(enabled=False, start_action=True)
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
