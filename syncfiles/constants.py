from enum import Enum


DATE_TIME_FORMAT = "%Y-%m-%d %I:%M %p"


class Mode(Enum):
    MIRROR = "mirror"
    ATOB = "atob"
    BTOA = "btoa"
