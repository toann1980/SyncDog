from functools import partial
from pathlib import Path

from logger import Logger

from syncdog.syncdog_ui import Ui_SyncDog

from PySide6 import (QtGui, QtWidgets)


filename = Path(__file__).stem
logger = Logger(filename)
logger.set_logging_level("debug")
logger.debug(f"\n{__file__=}")
logger.debug(f"{filename=}")


def cleanup_and_exit():
    QtWidgets.qApp.quit()


class SyncFilesWindow(QtWidgets.QMainWindow, Ui_SyncDog):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.alpha_path: Path = None
        self.beta_path: Path = None
        self.mode: str = None
        self.setup_user_interface()
        # self.syncer = SyncFiles(callback=self.syncer_messages)
        self.toggle_ready(False)

    def setup_user_interface(self) -> None:
        """
        Sets up the user interface by connecting buttons to their respective
        actions, initializing the system tray icon, and adjusting the visibility
        and size of UI elements.
        """
        self.button_a.clicked.connect(
            partial(self.button_path_action, "alpha"))
        self.button_b.clicked.connect(partial(self.button_path_action, "beta"))
        self.button_subfolder.clicked.connect(self.subfolder_action)
        self.button_action.clicked.connect(self.main_button_action)
        self.button_refresh.clicked.connect(self.refresh_button_action)
        self.button_AtoB.clicked.connect(partial(self.mode_switch, "atob"))
        self.button_BtoA.clicked.connect(partial(self.mode_switch, "btoa"))
        self.button_mirror.clicked.connect(partial(self.mode_switch, "mirror"))
        self.setup_tray()
        self.tray_icon.show()
        self.frame_subfolder.setVisible(False)
        self.resize(482, self.size().height())

    def setup_tray(self) -> None:
        """
        Sets up the system tray icon and its context menu.
        Initializes the tray icon with on and off states, connects the tray icon
        activation to an action handler, and creates a context menu with options
        to show, hide, and exit the application.
        """
        self.logo_on = QtGui.QIcon(str(Path("UI") / "sync.svg"))
        self.logo_off = QtGui.QIcon(str(Path("UI") / "sync.svg"))

        # Init QSystemTrayIcon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(self.logo_off))
        self.tray_icon.activated.connect(self.tray_icon_action)

        # - Tray Menu:
        self.hide_action = QtGui.QAction("Hide", self)
        self.hide_action.triggered.connect(self.hide)
        self.show_action = QtGui.QAction("Show", self)
        self.show_action.triggered.connect(self.show)
        self.quit_action = QtGui.QAction("Exit", self)
        self.quit_action.triggered.connect(cleanup_and_exit)
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
            logger.debug("DoubleClick")
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
        logger.debug(f"{button} button clicked.")
        if button == "alpha":
            current_label = self.label_a
            self.title = "A"
        else:
            current_label = self.label_b
            self.title = "B"
        current_path = self.select_path(
            caption=f"Select Directory {button[0].capitalize()}"
        )
        if current_path == "":
            current_label.setText(self.title)
        else:
            current_label.setText(current_path)
            current_path = current_path.replace("/", "\\")
            if button == "alpha":
                self.alpha_path = Path(current_path)
                # self.syncer.set_path(path=self.alpha_path, alpha=True)
            else:
                self.beta_path = Path(current_path)
                # self.syncer.set_path(path=self.beta_path, alpha=False)
            logger.debug(f"Current path {button} = {current_path}")

        self.check_ready_state()

    def check_ready_state(self) -> None:
        """
        Checks the ready state of the application and toggles the ready state
        accordingly.

        This method calls `self.state_ready()` to determine if the application
        is in a ready state. Based on the result, it enables or disables the
        ready state by calling `self.toggle_ready()`.
        """
        self.toggle_ready(enabled=self.state_ready())

    def confirm_start(self) -> bool:
        """
        Displays a confirmation message box to the user asking if they want to
        start syncing.
        Returns:
            bool: True if the user clicks 'OK', False otherwise.
        """
        self.msgBox = QtWidgets.QMessageBox()
        self.msgBox.setIcon(QtWidgets.QMessageBox.Information)
        self.msgBox.setText("Are you sure you want to start syncing?")
        self.msgBox.setWindowTitle("QtWidgets.QMessageBox Example")
        self.msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        self.returnValue = self.msgBox.exec()
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
            # self.syncer.stop = True
            self.button_action.setText("Synchronize")
            return

        self.button_refresh.setEnabled(False)
        logger.debug("main_button_action clicked.")
        if self.state_ready() and self.confirm_start():
            self.button_action.setText("Stop")
            # self.syncer.stop = False
            self.toggle_ready(enabled=False, start_action=True)

    def mode_switch(self, mode: str) -> None:
        """
        Switches the current mode of the application.

        Args:
            mode (str): The mode to switch to. Possible values are "mirror" and
                others.

        Returns:
            None
        """
        self.mode = mode
        logger.debug(f"Switching mode to {mode}.")
        self.mode = mode
        # self.syncer.set_mode(mode=self.mode)
        if self.mode == "mirror":
            self.checkBox_mirror.setChecked(False)
        self.toggle_ready(enabled=self.state_ready())

    def refresh_button_action(self) -> None:
        """
        Handles the action when the refresh button is clicked.

        Logs the action and triggers the main button action if syncing is not in
        progress.
        """
        logger.debug("refresh_button_action clicked.")
        if not self.syncher.syncing:
            self.main_button_action()

    def select_path(self, caption: str = "Select Directory", dir=None):
        return QtWidgets.QFileDialog.getExistingDirectory(
            self,
            caption=caption,
            dir=dir
        )

    def state_ready(self) -> bool:
        """
        Checks if the state is ready for processing.
        Returns:
            bool: True if the state is ready, False otherwise.
        """
        if self.alpha_path is None or self.beta_path is None:
            return False
        elif self.mode is None:
            return False
        elif self.alpha_path == self.beta_path:
            QtWidgets.QMessageBox.information(
                self, "Information", "Path A and B are the same!"
            )
            return False

        return True

    def subfolder_action(self) -> None:
        """
        Toggles the visibility of the subfolder frame. If the frame is currently
        visible, it will be hidden. If the frame is hidden, it will be made
        visible and the window will be resized to a width of 482 pixels while
        maintaining the current height.
        """
        if self.frame_subfolder.isVisible():
            self.frame_subfolder.setVisible(False)
        else:
            self.frame_subfolder.setVisible(True)
            self.resize(482, self.size().height())

    def syncer_messages(self, data: dict) -> None:
        """
        Handles messages from the syncer and updates the status bar.

        Args:
            data (dict): A dictionary containing message data. Expected to have
                a "status" key.

        Returns:
            None
        """
        logger.debug(f"{data=}")
        if data.get("status"):
            self.statusbar.showMessage(data["status"])

    def toggle_ready(self, enabled: bool, start_action: bool = False) -> None:
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
            self.button_refresh.setEnabled(enabled)
