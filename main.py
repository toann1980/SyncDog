from pathlib import Path
import sys

from logger import Logger
from syncdog.syncdog_window import SyncFilesWindow

from PySide6.QtWidgets import QApplication

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("debug")
logger.debug(f"\n{__file__=}")
logger.debug(f"{filename=}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = SyncFilesWindow()
    main_window.show()

    sys.exit(app.exec())
