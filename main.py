import asyncio
from pathlib import Path
import sys

from logger import Logger
from syncdog.SyncDogWindow import SyncFilesWindow

import qasync


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("debug")
logger.debug(f"\n{__file__ = }")
logger.debug(f"{filename = }")


if __name__ == "__main__":
    app = qasync.QApplication(sys.argv)

    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    main_window = SyncFilesWindow()
    main_window.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
