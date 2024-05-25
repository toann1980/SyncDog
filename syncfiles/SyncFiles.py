import asyncio
from concurrent.futures import ThreadPoolExecutor
import contextlib
from datetime import datetime
from pathlib import Path
import queue
from os import cpu_count
import time
import timeit
from typing import Literal

from .constants import *
from .utilities.interval import Interval
from getfiles import get_files
from logger import LoggingHandler

import aioshutil


filename = Path(__file__).stem
logger = LoggingHandler(logger_name=filename)
logger.set_logging_level("debug")
logger.debug(f"\n{__file__ = }")
logger.debug(f"{filename = }")


class SyncFiles:
    """
    A class used to synchronize files between two directories.

    Attributes:
        alpha_path (Path): The first directory path to be synchronized.
        beta_path (Path): The second directory path to be synchronized.
        callback_function (callable): A function to be called with a message
            dict when certain events occur.
        worker_count (int): The number of worker tasks to use for file
            operations.
        stop (bool): A flag to indicate whether the synchronization process
            should stop.
        interval (Interval): An interval object used to control the frequency
            of synchronization.

    Methods:
        calculate_time(): Calculates the total time taken for the
            synchronization task.
        callback(message: dict): Calls the callback function with the provided
            message.
        get_sync_files(path: Union[Path, str]) -> Dict[Path, datetime]: Returns
            a dictionary of file paths and their last modified times for the
            given directory.
        process_queue_item(): Processes a single item from the queue, performing
            the appropriate file operation.
    """    
    def __init__(self, callback: callable = None):
        super().__init__()
        self.alpha_path: Path = None
        self.beta_path: Path = None
        self.callback_function = callback
        self.worker_count: int = None
        self.stop = False
        self.interval = Interval()

    def calculate_time(self):
        """
        Calculates the total time taken for the synchronization task and logs
        the result.
        """        
        self.stop_time = timeit.default_timer()
        self.total_time = round(self.stop_time - self.start_time, 3)
        if self.total_time < 60:
            logger.info(f"Task took {self.total_time} seconds.\n")
        else:
            self.min_sec = \
                time.strftime("%H:%M:%S", time.gmtime(self.total_time))
            logger.info(
                f"Task took {self.min_sec.split(':')[1]} minutes,"
                f" {self.min_sec.split(':')[2]} seconds."
            )
        
    def callback(self, message: dict) -> None:
        """
        Calls the callback function with the provided message.

        Args:
            message (dict): The message to be passed to the callback function.
        """        
        if self.callback_function:
            self.callback_function(message)

    def get_sync_files(self, path: Path | str) -> dict[Path, datetime]:
        """
        Returns a dictionary of file paths and their last modified times for
        the given directory.

        Args:
            path (Union[Path, str]): The directory path to get the files from.

        Returns:
            Dict[Path, datetime]: A dictionary of file paths and their last
                modified times.
        """        
        if path.exists():
            files = get_files(path=str(path), as_date_time=True)
            return {
                entry["path"].relative_to(path).as_posix(): entry["datetime"]
                for entry in files
            }
        else:
            path.mkdir(parents=True, exist_ok=True)
            return {}

    async def process_queue_item(self):
        """
        Processes a single item from the queue, performing the appropriate file
        operation.
        """        
        while not self.stop:
            record = await self.queue.get()
            if record:
                instruction, *path = record
                if instruction == "delete":
                    try:
                        # Attempt to delete the file
                        Path(path[0]).unlink(missing_ok=True)
                        logger.debug(f"Deleted {path[0].name}")
                    except FileNotFoundError:
                        pass
                    except Exception as err:
                        logger.info(f"An error occurred: {str(err)}")
                elif instruction == "copy":
                    Path(path[1]).parent.mkdir(parents=True, exist_ok=True)
                    await aioshutil.copy2(str(path[0]), str(path[1]))
                    logger.debug(f"Copied {path[1].name}")
                with contextlib.suppress(ValueError):
                    self.queue.task_done()
            else:
                break

    async def queue_file_differences(
            self,
            source_path: Path | str,
            target_path: Path | str
    ) -> None:
        """
        Queues file operations based on the differences between the source and
        target directories.

        Args:
            source_path (Union[Path, str]): The source directory path.
            target_path (Union[Path, str]): The target directory path.
        """        
        def run_in_thread(queue_object):
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_source = \
                    executor.submit(self.get_sync_files, source_path)
                future_target = \
                    executor.submit(self.get_sync_files, target_path)
                source_files = future_source.result()
                target_files = future_target.result()
                queue_object.put((source_files, target_files))

        queue_object = queue.Queue()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_in_thread, queue_object)

        # Get the result from the queue
        source_files, target_files = queue_object.get()
            
        file_count = 0
        files_in_both = set()

        for file, timestamp in source_files.items():
            if file.endswith(".db"):
                continue
            elif target_files.get(file):
                files_in_both.add(file)
                if timestamp > target_files[file]:
                    file_count += 1
                    await self.queue.put(
                        ("copy", source_path / file, target_path / file)
                    )
            else:
                file_count += 1
                await self.queue.put(
                    ("copy", source_path / file, target_path / file)
                )

        for file in target_files.keys():
            if file not in files_in_both:
                file_count += 1
                await self.queue.put(
                    ("delete", target_path / file)
                )
        if file_count:
            self.callback(
                {"status": f"Queued {file_count} files. Copying files."}
            )

    async def queue_file_differences_mirror_mode(
            self,
            source_path: Path | str,
            target_path: Path | str
    ) -> None:
        """
        Queues up file operations for mirror mode, where the source and target
        directories should be identical.

        Args:
            source_path (Union[Path, str]): The source directory path.
            target_path (Union[Path, str]): The target directory path.
        """        
        source_files = self.get_sync_files(source_path)
        target_files = self.get_sync_files(target_path)
        file_count = 0
        files_in_both = set()

        for file, timestamp in source_files.items():
            if file.endswith(".db"):
                continue
            elif target_files.get(file):
                files_in_both.add(file)
                if timestamp > target_files[file]:
                    await self.queue.put(
                        ("copy", source_path / file, target_path / file)
                    )
                else:
                    await self.queue.put(
                        ("copy", target_path / file, source_path / file)
                    )
                file_count += 1
            else:
                await self.queue.put(("delete", source_path / file))

        for file, timestamp in target_files.items():
            if file not in files_in_both:
                await self.queue.put(("delete", target_path / file))

        self.callback(
            {"status": f"Queued {file_count} files. Copying files."}
        )

    def set_mode(self, mode: Literal["mirror", "atob", "btoa"]) -> None:
        """
        Sets the mode of operation for the synchronization process.

        Args:
            mode (Literal['mirror', 'atob', 'btoa']): The mode of operation.
        """        
        if mode == "mirror":
            self.mode = Mode.MIRROR
        elif mode == "atob":
            self.mode = Mode.ATOB
        elif mode == "btoa":
            self.mode = Mode.BTOA

    def set_path(self, path: Path | str, alpha: bool = True) -> None:
        """
        Sets either the alpha or beta path to the provided path.

        Args:
            path (Union[Path, str]): The path to set.
            alpha (bool, optional): Whether to set the alpha path. If False,
                sets the beta path. Defaults to True.
        """        
        if alpha:
            self.alpha_path = Path(path)
        else:
            self.beta_path = Path(path)

    async def repeated_sync(self) -> None:
        """
        Repeatedly synchronizes the files at the set interval until stopped.
        """        
        while not self.stop:
            await self.sync_files()
            await asyncio.sleep(self.interval.value)
            self.interval.set_next_interval()
            if self.interval.value < 61:
                logger.debug(
                    f"Next interval in {self.interval.value} seconds.\n"
                )
            else:
                logger.debug(
                    f"Next interval in {int(self.interval.value / 60)} "
                    "minutes.\n"
                )
    
    async def sync_files(self):
        """
        Synchronizes the files between the alpha and beta paths based on the set
            mode.
        """        
        logger.debug(f"sync mode: {self.mode}")
        logger.info(
            f"sync started at {datetime.now().strftime(DATE_TIME_FORMAT)}"
        )
        self.start_time = timeit.default_timer()

        self.queue = asyncio.Queue()
        async with asyncio.TaskGroup() as task_group:
            await task_group.create_task(self.sync_files_windows())
            
            
            logger.debug(f"self.queue count: {self.queue.qsize()}")
            if self.queue.qsize() == 0:
                self.callback({"status": "No files to sync."})
                return
            self.interval.reset()
            self.worker_count = min(cpu_count(), self.queue.qsize())
            for _ in range(self.worker_count):
                await self.queue.put(None)
            for _ in range(self.worker_count):
                if self.stop:
                    break                
                await task_group.create_task(self.process_queue_item())
        self.end_message = \
            f"Sync ended at {datetime.now().strftime(DATE_TIME_FORMAT)}"
        logger.info(self.end_message)
        self.callback({"status": self.end_message})
        
        self.calculate_time()

    async def sync_files_windows(self):
        """
        Synchronizes the files between the alpha and beta paths based on the
            set mode, specifically for Windows.
        """        
        if self.mode == Mode.MIRROR:
            await self.queue_file_differences_mirror_mode(
                self.alpha_path, self.beta_path
            )
        else:
            if self.mode == Mode.ATOB:
                self.run_kwargs = {
                    "source_path":self.alpha_path, "target_path": self.beta_path
                }
            elif self.mode == Mode.BTOA:
                self.run_kwargs = {
                    "source_path":self.beta_path, "target_path": self.alpha_path
                }
            await self.queue_file_differences(**self.run_kwargs)
