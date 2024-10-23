import contextlib
import os
from pathlib import Path
import shutil
import time
import threading
from typing import Union
from syncdog.base_handler import BaseHandler

from logger import Logger

from syncdog.constants import FileSystemEvents

filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")

class MirrorHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        self.folder_a = None
        self.folder_b = None
        self.debounce_interval = 0.5
        self._last_sync = time.time()
        
    def on_any_event(self, event: FileSystemEvents):
        with self.lock:
            if self.folder_a is None or self.folder_b is None:
                return

            src_path = Path(event.src_path)
            if '.syncdog' in src_path.parts:
                return
            match event.event_type:
                case FileSystemEvents.CREATED.value:
                    if event.is_directory:
                        self.copy_directory(event.event_type, src_path)
                    else:
                        self.track_file_copy(event.event_type, src_path)
                case FileSystemEvents.DELETED.value:
                    self.delete(src_path)
                case FileSystemEvents.MOVED.value:
                    self.rename(event)
                case FileSystemEvents.MODIFIED.value:
                    if self.copying_files.get(src_path):
                        return
                    self.track_file_copy(event.event_type, src_path)
                    
    def get_src_dest_paths(
        self,
        origin: str,
        src_path: Union[Path, str]
    ) -> tuple[Path, Path]:
        ...
    
    # TODO: creat check_ignore_event for seeing if event is a bounce event