import os
import unittest
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
        self.window = SyncFilesWindow(
            observer_class=SyncDogObserver,
            file_handler_class=SyncDogFileHandler
        )
        self.window.show()

    def test_initial_state(self):
        # Check initial state of the window
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.windowTitle(), 'SyncDog')

        self.assertEqual(self.window.mode, SyncMode.IDLE)

    def test_initial_state_buttons(self):
        # Initial state of buttons
        button_a = self.window.findChild(QtWidgets.QPushButton, 'button_a')
        self.assertIsNotNone(button_a)
        self.assertTrue(button_a.isEnabled())
        self.assertEqual(button_a.text(), '...')

        button_b = self.window.findChild(QtWidgets.QPushButton, 'button_b')
        self.assertIsNotNone(button_b)
        self.assertTrue(button_b.isEnabled())
        self.assertEqual(button_b.text(), '...')

        button_AtoB = self.window.findChild(
            QtWidgets.QPushButton, 'button_AtoB')
        self.assertIsNotNone(button_AtoB)
        self.assertTrue(button_AtoB.isEnabled())
        self.assertEqual(button_AtoB.text(), 'A to B')

        button_BtoA = self.window.findChild(
            QtWidgets.QPushButton, 'button_BtoA')
        self.assertIsNotNone(button_BtoA)
        self.assertTrue(button_BtoA.isEnabled())
        self.assertEqual(button_BtoA.text(), 'B to A')

        button_mirror = self.window.findChild(
            QtWidgets.QPushButton, 'button_mirror')
        self.assertIsNotNone(button_mirror)
        self.assertTrue(button_BtoA.isEnabled())
        self.assertEqual(button_mirror.text(), 'Mirror')

        button_main = self.window.findChild(
            QtWidgets.QPushButton, 'button_action')
        self.assertIsNotNone(button_main)
        self.assertFalse(button_main.isEnabled())
        self.assertEqual(button_main.text(), 'Synchronize')

        button_refresh = self.window.findChild(
            QtWidgets.QPushButton, 'button_refresh')
        self.assertIsNotNone(button_refresh)
        self.assertFalse(button_refresh.isEnabled())
        self.assertEqual(button_refresh.text(), 'Refresh')

    def test_initial_tray(self):
        tray_icon = self.window.findChild(
            QtWidgets.QSystemTrayIcon, 'tray_icon')
        self.assertIsNotNone(tray_icon)
        self.assertEqual(tray_icon.isVisible(), True)
        # self.assertEqual()

    def test_intiial_state_statusbar(self):
        # Initial state of the mode
        statusbar = self.window.findChild(
            QtWidgets.QStatusBar, 'statusbar')
        self.assertIsNotNone(statusbar)
        self.assertEqual(statusbar.currentMessage(), '')

    def test_button_click(self):
        # Simulate button click and check the outcome
        button = self.window.findChild(QtWidgets.QPushButton, 'button_AtoB')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.ATOB)

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
