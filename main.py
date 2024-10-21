from pathlib import Path
import sys
import threading

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from syncdog.constants import SyncMode
from syncdog.syncdog_window import SyncFilesWindow
from syncdog.syncdog_observer import SyncDogObserver
from syncdog.syncdog_file_handler import SyncDogFileHandler
from watchdog.observers.api import BaseObserver
from watchdog.events import FileSystemEventHandler


@Slot(object, Path, Path)
def start_syncing(mode, source: Path, destination: Path) -> None:
    match mode:
        case SyncMode.ATOB:
            handler.change_source(source)
            handler.change_destination(destination)
            observer.change_directory(source)
        case SyncMode.BTOA:
            handler.change_source(destination)
            handler.change_destination(source)
            observer.change_directory(destination)
        case SyncMode.MIRROR:
            ...

    threading.Thread(target=observer.run).start()


def stop_observer(
        observer: BaseObserver,
        handler: FileSystemEventHandler
) -> None:
    observer.stop()
    handler.cleanup()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    handler = SyncDogFileHandler()
    observer = SyncDogObserver(file_handler=handler)
    mirror_handler = SyncDogFileHandler()
    mirror_observer = SyncDogObserver(file_handler=mirror_handler)

    main_window = SyncFilesWindow()
    # Connect signals to start and stop the observer
    main_window.start_observer_signal.connect(start_syncing)
    main_window.stop_observer_signal.connect(
        lambda: stop_observer(observer, handler)
    )

    main_window.show()

    sys.exit(app.exec())
