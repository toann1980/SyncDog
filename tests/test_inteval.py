import unittest
from syncdog.utils.interval import BackoffInterval


class TestInterval(unittest.TestCase):
    def test_initialization(self):
        interval = BackoffInterval()
        assert interval.min_interval == 1
        assert interval.max_interval == 60
        assert interval.delay_times == 0
        assert interval.delay_wait == 15
        assert interval.value == 1

    def test_reset(self):
        interval = BackoffInterval()
        interval._value = 30
        interval.delay_times = 10
        interval.reset()
        assert interval.value == 1
        assert interval.delay_times == 0

    def test_set_next(self):
        interval = BackoffInterval()
        interval.set_next()
        assert interval.value == 1
        assert interval.delay_times == 1

        interval.delay_times = 15
        interval.set_next()
        assert interval.value == 15

    def test_set_max(self):
        interval = BackoffInterval()
        interval.set_max(120)
        assert interval.max_interval == 120

    def test_value_property(self):
        interval = BackoffInterval()
        interval._value = 30
        assert interval.value == 30
