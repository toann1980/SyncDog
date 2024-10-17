import sys

from PySide6.QtWidgets import QApplication

from syncdog.syncdog_window import SyncFilesWindow
from syncdog.syncdog_observer import SyncDogObserver
from syncdog.syncdog_file_handler import SyncDogFileHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = SyncFilesWindow(
        event_handler_class=SyncDogFileHandler,
        observer_class=SyncDogObserver
    )
    main_window.show()

    sys.exit(app.exec())
