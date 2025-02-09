from functools import partial
import os
import sys
from pathlib import Path
from typing import Literal

from logger import Logger
from syncdog.ui import Ui_SyncDog
from syncdog.constants import SyncMode

from PySide6 import (QtCore, QtGui, QtWidgets)


filename = Path(__file__).stem
logger = Logger(filename)
logger.set_logging_level("debug")
logger.debug(f"\n{__file__=}")
logger.debug(f"{filename=}")


if hasattr(sys, "_MEIPASS"):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(".")


class SyncDogWindow(QtWidgets.QMainWindow, Ui_SyncDog):
    start_observer_signal = QtCore.Signal(object, Path, Path)
    stop_observer_signal = QtCore.Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setup_user_interface()
        self.alpha_path: Path = None
        self.beta_path: Path = None
        self.mode: SyncMode = SyncMode.IDLE
        self.toggle_buttons_enabled(False)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        """
        Overrides the changeEvent to hide the window when it is minimized.
        """
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                self.hide()
        super().changeEvent(event)

    def closeEvent(self, event) -> None:
        """
        Overrides the closeEvent to display a confirmation dialog.
        If the user confirms, the application will close; otherwise, it will
        remain open.
        """
        if os.getenv('UNIT_TESTING'):
            event.accept()
            return

        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setWindowTitle("Confirm Quit")
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        msgBox.setObjectName("confirmQuitMessageBox")

        reply = msgBox.exec()
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def setup_user_interface(self) -> None:
        """
        Sets up the user interface by connecting buttons to their respective
        actions, initializing the system tray icon, and adjusting the visibility
        and size of UI elements.
        """
        self.button_a.clicked.connect(
            partial(self.button_path_action, "alpha"))
        self.button_b.clicked.connect(partial(self.button_path_action, "beta"))
        self.button_action.clicked.connect(self.main_button_action)
        self.button_AtoB.clicked.connect(partial(self.mode_switch, "atob"))
        self.button_BtoA.clicked.connect(partial(self.mode_switch, "btoa"))
        self.button_mirror.clicked.connect(partial(self.mode_switch, "mirror"))
        self.setup_tray()
        self.tray_icon.show()
        self.resize(482, self.size().height())
        self.setWindowIcon(
            QtGui.QIcon(str(base_path / "UI" / "syncdog-icon_64.ico"))
        )

    def setup_tray(self) -> None:
        """
        Sets up the system tray icon and its context menu.
        Initializes the tray icon with on and off states, connects the tray icon
        activation to an action handler, and creates a context menu with options
        to show, hide, and exit the application.
        """
        self.logo_off = str(base_path / "UI" / "sync_off.svg")

        # Init QSystemTrayIcon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setObjectName("tray_icon")
        self.tray_icon.setIcon(QtGui.QIcon(self.logo_off))
        self.tray_icon.activated.connect(self.tray_icon_action)

        # Tray Menu:
        self.hide_action = QtGui.QAction("Hide", self)
        self.hide_action.triggered.connect(self.hide)
        self.show_action = QtGui.QAction("Show", self)
        self.show_action.triggered.connect(self.show)
        self.quit_action = QtGui.QAction("Exit", self)
        self.quit_action.triggered.connect(self.close)
        self.tray_menu = QtWidgets.QMenu()
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

    def tray_icon_action(self, event) -> None:
        """
        Handles the tray icon action event.

        If the event is a double-click on the system tray icon, it raises and
        shows the main window.

        Args:
            event: The event triggered by the system tray icon.
        """
        if event == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.raise_()
            self.show()

    def button_path_action(self, button: str) -> None:
        """
        Handles the action when a button is clicked to select a directory path.
        Args:
            button (str): The identifier of the button clicked. Expected values
                are "alpha" or "beta".
        Returns:
            None
        Side Effects:
            - Updates the title and label based on the button clicked.
            - Opens a dialog to select a directory path.
            - Updates the internal path variables (`alpha_path` or `beta_path`)
                based on the selected path.
            - Logs debug information about the button clicked and the selected
                path.
            - Calls `check_ready_state` to update the state of the application.
        """
        dir = None
        if button == "alpha":
            current_label = self.label_a
            if os.getenv('GUI_TESTING'):
                dir = r"C:\tmp\SyncDogTest"
        else:
            current_label = self.label_b
            if os.getenv('GUI_TESTING'):
                dir = r"C:\tmp\SyncDogTest_Dest"
        current_path = self.select_path(
            caption=f"Select Directory {button[0].capitalize()}", dir=dir
        )
        if current_path == "":
            if (button == "alpha" and self.alpha_path is None) or \
                    (button == "beta" and self.beta_path is None):
                current_label.setText('Select a directory...')
        else:
            current_path = current_path.replace("/", "\\")
            current_label.setText(current_path)
            if button == "alpha":
                self.alpha_path = Path(current_path)
            else:
                self.beta_path = Path(current_path)

        self.toggle_buttons_enabled(enabled=self.state_ready())

    def confirm_start(self) -> bool:
        """
        Displays a confirmation message box to the user asking if they want to
        start syncing.
        Returns:
            bool: True if the user clicks 'OK', False otherwise.
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText("Are you sure you want to start syncing?")
        msgBox.setWindowTitle("Confirm Start")
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        msgBox.setObjectName("confirmStartMessageBox")
        self.returnValue = msgBox.exec()
        if self.returnValue == QtWidgets.QMessageBox.Ok:
            print('OK clicked')
            return True

        return False

    def main_button_action(self) -> None:
        """
        Handles the main button action for starting or stopping synchronization.
        If the button text is "Stop", it sets the button text to "Synchronize"
        and returns. Otherwise, it disables the refresh button, logs the action,
        and if the state is ready and the start is confirmed, it sets the button
        text to "Stop" and toggles the ready state.
        """
        if self.button_action.text() == "Stop":
            self.stop_observer_signal.emit()
            self.set_tray_icon("off")
            self.button_action.setText("Synchronize")
            self.toggle_buttons_enabled(enabled=True, start_action=True)
            return

        if self.state_ready() and self.confirm_start():
            self.set_tray_icon(self.mode.value)
            self.button_action.setText("Stop")
            self.toggle_buttons_enabled(enabled=False, start_action=True)
            self.start_observer_signal.emit(*self.set_directories())

    def mode_switch(self, mode: str) -> None:
        """
        Switches the current mode of the application.

        Args:
            mode (str): The mode to switch to. Possible values are "mirror" and
                others.

        Returns:
            None
        """
        match mode:
            case "atob":
                self.mode = SyncMode.ATOB
            case "btoa":
                self.mode = SyncMode.BTOA
            case "mirror":
                self.mode = SyncMode.MIRROR
        self.toggle_buttons_enabled(enabled=self.state_ready())
        self.update_styles()

    def select_path(self, caption: str = "Select Directory", dir=None):
        return QtWidgets.QFileDialog.getExistingDirectory(
            self,
            caption=caption,
            dir=dir
        )

    def set_directories(self) -> None:
        match self.mode:
            case SyncMode.ATOB:
                source = self.alpha_path
                destination = self.beta_path
            case SyncMode.BTOA:
                source = self.beta_path
                destination = self.alpha_path
            case SyncMode.MIRROR:
                source = self.alpha_path
                destination = self.beta_path
        return (self.mode, source, destination)

    def set_tray_icon(
            self,
            action: Literal["off", "atob", "btoa", "mirror"]
    ) -> None:
        if action == "off":
            icon = self.logo_off
        else:
            icon = str(base_path / "UI" / f"sync_{action}.svg")
        self.tray_icon.setIcon(QtGui.QIcon(icon))

    def state_ready(self) -> bool:
        """
        Checks if the state is ready for processing.
        Returns:
            bool: True if the state is ready, False otherwise.
        """
        if self.alpha_path is None or self.beta_path is None or \
                self.mode == SyncMode.IDLE:
            return False
        elif self.alpha_path == self.beta_path:
            QtWidgets.QMessageBox.information(
                self, "Information", "Path A and B are the same!"
            )
            return False

        return True

    def toggle_buttons_enabled(
            self,
            enabled: bool,
            start_action: bool = False
    ) -> None:
        """
        Toggles the enabled state of various buttons in the UI.

        Args:
            enabled (bool): The state to set the buttons to (True for enabled,
                False for disabled).
            start_action (bool, optional): If True, toggles a specific set of
                buttons related to starting an action. If False, toggles a
                different set of buttons. Defaults to False.

        Returns:
            None
        """
        if start_action:
            self.button_a.setEnabled(enabled)
            self.button_b.setEnabled(enabled)
            self.button_AtoB.setEnabled(enabled)
            self.button_BtoA.setEnabled(enabled)
            self.button_mirror.setEnabled(enabled)
        else:
            self.button_action.setEnabled(enabled)

    def update_styles(self) -> None:
        for button in [self.button_AtoB, self.button_BtoA, self.button_mirror]:
            button.setStyleSheet('')

        depressed_buttons_style = 'QPushButton { text-decoration: underline; ' \
            'color: #7DF9FF; font-weight: bold; }'
        match self.mode:
            case SyncMode.ATOB:
                self.button_AtoB.setStyleSheet(depressed_buttons_style)
            case SyncMode.BTOA:
                self.button_BtoA.setStyleSheet(depressed_buttons_style)
            case SyncMode.MIRROR:
                self.button_mirror.setStyleSheet(depressed_buttons_style)
