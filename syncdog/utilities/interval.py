TWO_MINUTES = 2 * 60
FIVE_MINUTES = 5 * 60
TEN_MINUTES = 10 * 60
FIFTEEN_MINUTES = 15 * 60
THIRTY_MINUTES = 30 * 60
ONE_HOUR = 60 * 60
LONG_INTERVALS = {
    60: TWO_MINUTES,
    TWO_MINUTES: FIVE_MINUTES,
    FIVE_MINUTES: TEN_MINUTES,
    TEN_MINUTES: FIFTEEN_MINUTES,
    FIFTEEN_MINUTES: THIRTY_MINUTES,
    THIRTY_MINUTES: ONE_HOUR,
    ONE_HOUR: ONE_HOUR
}


class Interval:
    """
    A class used to represent an interval with a interval that increases over
    time.

    Attributes:
        value (int): The current value of the interval.
        delay_wait (int): The number of times to delay before increasing the
            interval.
        delay_times (int): The number of times the interval has been delayed.

    Methods:
        set_next_interval: Determines the next interval value based on the
            current state.
        set_next: Sets the next interval value.
        reset: Resets the interval value to 1.
    """

    def __init__(
            self,
            min_interval: int = 1,
            max_interval: int = 60,
            backoff_factor: float = 2.0,
            delay_wait: int = 30
    ) -> None:
        """
        Args:
            min_interval (int, optional): The minimum value of the interval in
                seconds. Defaults to 1.
            max_interval (int, optional): The maximum value of the interval in
                seconds. Defaults to 60.
            backoff_factor (float, optional): The factor by which the interval
                increases. Defaults to 2.0.
            delay_wait (int, optional): The number of times to delay before
                increasing the interval. Defaults to 5.
        """        
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.backoff_factor = backoff_factor
        self.delay_wait = delay_wait
        self.value = min_interval
        self.delay_times = 0

    def set_next_interval(self) -> int:
        """
        Determines the next interval value based on the current state.

        Returns:
            int: The next interval value.
        """
        if self.value == self.min_interval:
            if self.delay_times < self.delay_wait:
                self.delay_times += 1
            else:
                self.value = min(
                    self.value * self.backoff_factor, self.max_interval
                )
        elif self.value < self.max_interval:
            self.value = min(
                self.value * self.backoff_factor, self.max_interval
            )

    def set_next(self) -> int:
        """
        Sets the next interval value and returns it.

        Returns:
            int: The new interval value.
        """
        self.value = self.set_next_interval()

    def reset(self) -> None:
        """Resets the interval value to 1.
        """
        self.value = 1
