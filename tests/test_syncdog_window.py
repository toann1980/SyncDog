import unittest
from PySide6 import QtTest, QtCore, QtWidgets
from syncdog.syncdog_window import SyncFilesWindow
from syncdog.syncdog_observer import SyncDogObserver
from syncdog.syncdog_file_handler import SyncDogFileHandler
from syncdog.constants import SyncMode


class TestSyncFilesWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication([])

    def setUp(self):
        self.window = SyncFilesWindow(
            observer_class=SyncDogObserver,
            file_handler_class=SyncDogFileHandler
        )
        self.window.show()

    def test_initial_state(self):
        # Check initial state of the window
        self.assertTrue(self.window.isVisible())
        print(f'windowTitle: {self.window.windowTitle()}')
        self.assertEqual(self.window.windowTitle(), "SyncDog")

    def test_button_click(self):
        # Simulate button click and check the outcome
        button = self.window.findChild(QtWidgets.QPushButton, 'button_AtoB')
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        self.assertEqual(self.window.mode, SyncMode.ATOB)

    def tearDown(self):
        self.window.close()

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        QtCore.QCoreApplication.quit()
