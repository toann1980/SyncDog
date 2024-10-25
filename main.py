from pathlib import Path
import sys
import threading

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

from syncdog.constants import SyncMode
from syncdog.window import SyncDogWindow
from syncdog.observer import SyncDogObserver
from syncdog.file_handler import FileHandler
from syncdog.mirror_handler import MirrorHandler


handler = FileHandler()
mirror_handler = MirrorHandler()
observer = SyncDogObserver()


@Slot(object, Path, Path)
def start_syncing(mode, dir_a: Path, dir_b: Path) -> None:
    match mode:
        case SyncMode.ATOB | SyncMode.BTOA:
            handler.set_source(dir_a)
            handler.set_destination(dir_b)
            observer.set_handler(handler)
            observer.set_directory(dir_a)
        case SyncMode.MIRROR:
            mirror_handler.set_dir_a(dir_a)
            mirror_handler.set_dir_b(dir_b)
            observer.set_handler(mirror_handler)
            observer.set_directory([dir_a, dir_b])

    threading.Thread(target=observer.run).start()


def stop_observer() -> None:
    observer.stop()
    handler.cleanup()
    mirror_handler.cleanup()


def main() -> None:
    app = QApplication(sys.argv)

    main_window = SyncDogWindow()
    main_window.start_observer_signal.connect(start_syncing)
    main_window.stop_observer_signal.connect(stop_observer)
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
