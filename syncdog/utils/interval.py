from dataclasses import dataclass, field
from enum import Enum


NEXT_INTERVAL = {
    1: 15,
    15: 30,
    30: 60,
    60: 120,
    120: 300,
    300: 600,
    600: 900,
    900: 1800,
    1800: 3600,
    3600: 3600,
}


@dataclass
class BackoffInterval:
    """
    A class used to represent an interval with a interval that increases over
    time.

    Attributes:
        min_interval (int): The minimum amount of the interval.
        max_interval (int): The maximum amount of the interval.
        delay_wait (int): The number of times to delay before increasing the
            interval.
        _value (int): The current interval amount.

    Methods:
        set_next_interval: Determines the next interval value based on the
            current state.
        reset: Resets the interval value to the minimum interval.
        set_max_interval: Sets the maximum interval value.
    """
    
    min_interval: int = 1
    max_interval: int = 60
    delay_times: int = field(default=0)
    delay_wait: int = 15
    _value: int = field(default=1)

    def reset(self) -> None:
        """Resets the interval value to the minimum interval.
        """
        self._value = self.min_interval
        self.delay_times = 0

    def set_next(self) -> None:
        """
        Determines the next interval value based on the current state.
        """
        if self.delay_times < self.delay_wait:
            self.delay_times += 1
        else:
            self._value = NEXT_INTERVAL.get(self._value, self.max_interval)

    def set_max(self, max_interval: int) -> None:
        """
        Sets the maximum interval value.

        Args:
            max_interval (int): The new maximum interval value.
        """
        self.max_interval = max_interval

    @property
    def value(self) -> int:
        """Gets the current interval value.
        """
        return self._value
