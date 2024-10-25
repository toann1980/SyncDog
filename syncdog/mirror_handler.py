
from contextlib import suppress
from pathlib import Path
import shutil
from typing import Union

from logger import Logger
from syncdog.base_handler import BaseHandler
from syncdog.constants import FileSystemEvents


filename = Path(__file__).stem
logger = Logger(logger_name=filename)
logger.set_logging_level("DEBUG")


class MirrorHandler(BaseHandler):
    def __init__(
        self,
        dir_a: Union[str, Path] = None,
        dir_b: Union[str, Path] = None,
        debounce_interval: float = 0.75
    ) -> None:
        """
        Initializes the MirrorHandler with directories and debounce interval.

        Args:
            dir_a (Union[str, Path], optional): Path to the first directory.
            dir_b (Union[str, Path], optional): Path to the second directory.
            debounce_interval (float, optional): Interval to debounce events.
        """
        super().__init__()
        self.dir_a: Path = None
        self.patch_path_a: Path = None
        if dir_a:
            self.set_dir_a(dir_a)
        self.dir_b: Path = None
        self.patch_path_b: Path = None
        if dir_b:
            self.set_dir_b(dir_b)
        self.debounce_interval = debounce_interval

    def on_any_event(self, event: FileSystemEvents):
        """
        Handles any file system event.

        Args:
            event (FileSystemEvents): The file system event that triggered this
                handler.
        """
        if self.dir_a is None or self.dir_b is None:
            return

        source_path = Path(event.src_path)
        if '.syncdog' in source_path.parts:
            return
        if self.working_files.get(source_path):
            return
        source, patch_path = self.get_directories(source_path)
        dest = self.dir_b if source == self.dir_a else self.dir_a
        match event.event_type:
            case FileSystemEvents.CREATED.value:
                if event.is_directory:
                    self.create_directory(source, source_path, dest)
                else:
                    self.track_work_file(
                        event.event_type, source, source_path, dest, patch_path)
            case FileSystemEvents.DELETED.value:
                self.delete(source, source_path, dest)
            case FileSystemEvents.MOVED.value:
                self.rename(event, source, dest)
            case FileSystemEvents.MODIFIED.value:
                if event.is_directory:
                    return
                dest_path = self.get_dest_path(source, source_path, dest)
                if dest_path.exists():
                    if dest_path.stat().st_size == source_path.stat().st_size:
                        return
                    else:
                        self.working_files[dest_path] = \
                            dest_path.stat().st_size
                self.track_work_file(
                    event.event_type, source, source_path, dest, patch_path)

    def cleanup(self) -> None:
        """
        Cleans up patch directories.
        """
        for path in [self.patch_path_a, self.patch_path_b]:
            if path and path.exists():
                shutil.rmtree(path, ignore_errors=True)
                path = None

    def get_directories(self, path: Path) -> Path:
        """
        Determines the source and patch directories based on the given path.

        Args:
            path (Path): The path to check.

        Returns:
            Path: The source and patch directories.

        Raises:
            ValueError: If either directory A or directory B is not set.
        """
        if self.dir_a is None:
            raise ValueError("Directory A is not set.")
        if self.dir_b is None:
            raise ValueError("Directory B is not set.")

        with suppress(ValueError):
            if path.relative_to(self.dir_a):
                return self.dir_a, self.patch_path_b

        return self.dir_b, self.patch_path_a

    def set_dir(
        self,
        dir_attr: str,
        dir_value: Union[str, Path],
        patch_attr: str
    ) -> None:
        """
        Sets the directory and its corresponding patch path.

        Args:
            dir_attr (str): The attribute name for the directory.
            dir_value (Union[str, Path]): The path to the directory.
            patch_attr (str): The attribute name for the patch path.
        """
        setattr(self, dir_attr, Path(dir_value))
        patch_path = getattr(self, patch_attr)
        if patch_path and patch_path.exists():
            patch_path.rmdir()
        new_patch_path = getattr(self, dir_attr) / ".syncdog"
        setattr(self, patch_attr, new_patch_path)
        new_patch_path.mkdir(exist_ok=True)

    def set_dir_a(self, dir_a: Union[str, Path]) -> None:
        """
        Sets the first directory and its patch path.

        Args:
            dir_a (Union[str, Path]): The path to the first directory.
        """
        self.set_dir('dir_a', dir_a, 'patch_path_a')

    def set_dir_b(self, dir_b: Union[str, Path]) -> None:
        """
        Sets the second directory and its patch path.

        Args:
            dir_b (Union[str, Path]): The path to the second directory.
        """
        self.set_dir('dir_b', dir_b, 'patch_path_b')
