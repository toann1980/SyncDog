import os
from pathlib import Path
import unittest
from unittest.mock import patch

from PySide6 import QtTest, QtCore, QtWidgets
from syncdog.syncdog_window import SyncFilesWindow
from syncdog.syncdog_observer import SyncDogObserver
from syncdog.syncdog_file_handler import SyncDogFileHandler
from syncdog.constants import SyncMode
from typing import Literal


class TestSyncFilesWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QtWidgets.QApplication.instance():
            cls.app = QtWidgets.QApplication([])
        else:
            cls.app = QtWidgets.QApplication.instance()

    def setUp(self):
        os.environ['UNIT_TESTING'] = '1'
        self.window = SyncFilesWindow()
        self.window.show()

    def test_initial_state(self):
        # Check initial state of the window
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.windowTitle(), 'SyncDog')

        self.assertEqual(self.window.mode, SyncMode.IDLE)

    def test_initial_state_buttons(self):
        # Initial state of buttons
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

    def test_initial_tray(self):
        tray_icon = self.window.findChild(
            QtWidgets.QSystemTrayIcon, 'tray_icon')
        self.assertIsNotNone(tray_icon)
        self.assertEqual(tray_icon.isVisible(), True)
        # self.assertEqual()

    def test_tray_icon_action(self):
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

    def test_intiial_state_statusbar(self):
        statusbar = self.window.findChild(
            QtWidgets.QStatusBar, 'statusbar')
        self.assertIsNotNone(statusbar)
        self.assertEqual(statusbar.currentMessage(), '')

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_alpha(self, mock_get_existing_directory):
        # Simulate setting the environment variable for GUI testing
        mock_get_existing_directory.return_value = r"C:\tmp\SyncDogTest"

        # Find the button and simulate a click
        button = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        # Verify the label and internal path are updated correctly
        self.assertEqual(self.window.label_a.text(), r"C:\tmp\SyncDogTest")
        self.assertEqual(self.window.alpha_path, Path(r"C:\tmp\SyncDogTest"))

    @patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_button_path_action_beta(self, mock_get_existing_directory):
        mock_get_existing_directory.return_value = r"C:\SyncDogTest_Dest"

        # Find the button and simulate a click
        button = self.window.findChild(QtWidgets.QPushButton, 'button_b')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)

        # Verify the label and internal path are updated correctly
        self.assertEqual(
            self.window.label_b.text(),
            r"C:\SyncDogTest_Dest"
        )
        self.assertEqual(
            self.window.beta_path,
            Path(r"C:\SyncDogTest_Dest")
        )

    def test_button_click_a_to_b(self):
        # Simulate button click and check the outcome
        button = self.window.findChild(QtWidgets.QPushButton, 'button_AtoB')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.ATOB)

    def test_button_click_b_to_a(self):
        button = self.window.findChild(QtWidgets.QPushButton, 'button_BtoA')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.BTOA)

    def test_button_click_mirror(self):
        ...

    def close_active_modal(self, button: Literal['yes', 'no'] = 'no') -> None:
        message_box = self.window.findChild(
            QtWidgets.QMessageBox, "confirmQuitMessageBox")
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

    def test_close_event_no_button(self):
        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())

        QtCore.QTimer.singleShot(250, lambda: self.close_active_modal('no'))
        self.window.close()

        os.environ['UNIT_TESTING'] = '1'

    def test_close_event_yes_button(self):
        del os.environ['UNIT_TESTING']
        self.assertTrue(self.window.isVisible())

        QtCore.QTimer.singleShot(250, lambda: self.close_active_modal('yes'))
        self.window.close()
        os.environ['UNIT_TESTING'] = '1'

    def tearDown(self):
        self.window.close()

    @classmethod
    def tearDownClass(cls):
        if QtWidgets.QApplication.instance():
            cls.app.quit()
            QtCore.QCoreApplication.quit()


if __name__ == "__main__":
    unittest.main()
