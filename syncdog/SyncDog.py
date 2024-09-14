from datetime import datetime
import threading
from pathlib import Path
import time
from logger import Logger

from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class SyncDogHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.file_timers = {}

    def handle_event(self, event: FileSystemEvent) -> None:
        logger.debug(f"time: {datetime.now()}")
        logger.debug(f"{event.src_path = }")
        logger.debug(f"{event.dest_path = }")
        logger.debug(f"{event.is_directory = }")
        # logger.debug(f"{event.is_synthetic = }\n")
        logger.debug(f"{event.event_type = }")
        file_path = Path(event.src_path)
        match event.event_type:
            case "created":
                self.handled_created(event)
                logger.debug(f"File {file_path.name} created")
            case "modified":
                logger.debug(f"File {file_path.name} modified")
            case "moved":
                logger.debug(f"File {file_path.name} moved")
            case "deleted":
                logger.debug(f"File {file_path.name} deleted")
            case _:
                logger.debug(f"File {file_path.name} {event.event_type}")

    def on_any_event(self, event):
        if event.src_path in self.file_timers and \
                self.file_timers[event.src_path] is not None:
            logger.debug(f"Canceling task for file {Path(event.src_path).stem}")
            self.file_timers[event.src_path].cancel()
            del self.file_timers[event.src_path]

        # Start a new timer
        self.file_timers[event.src_path] = threading.Timer(
            1.0, self.handle_event, args=[event]
        )
        self.file_timers[event.src_path].start()

    def handled_created(self, event: FileSystemEvent) -> None:
        logger.debug(f"{event.src_path = }")
        logger.debug(f"{event.dest_path = }")
        logger.debug(f"{event.event_type = }")
        logger.debug(f"{event.is_directory = }")
        logger.debug(f"{event.is_synthetic = }\n")


class SyncDogObserver:
    def __init__(
        self,
        directory: Path | str,
        handler: FileSystemEventHandler = SyncDogHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True
        )
        self.observer.start()
        logger.debug("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        logger.debug("\nWatcher Terminated\n")
