from enum import Enum


DATE_TIME_FORMAT = "%Y-%m-%d %I:%M %p"


class FileSystemEvents(Enum):
    MOVED: str = 'moved'
    DELETED: str = 'deleted'
    CREATED: str = 'created'
    MODIFIED: str = 'modified'
    CLOSED: str = 'closed'
    CLOSED_NO_WRITE: str = 'closed_no_write'
    OPENED: str = 'opened'


class SyncMode(Enum):
    MIRROR = "mirror"
    ATOB = "atob"
    BTOA = "btoa"
    IDLE = "idle"
