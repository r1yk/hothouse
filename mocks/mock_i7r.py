"""Mock implemntations of i7r + devices"""

from datetime import datetime
import math
from i7r import Environment, Fan, Heater, Humidifier, Light


class MockFan(Fan):
    """Mock fan"""

    def fan_on(self, level=1):
        print(f'Setting fan to {level}')

    def fan_off(self) -> None:
        print('fan off')


class MockHeater(Heater):
    """Mock heater"""

    def heat_on(self, level=1):
        print(f'Setting heat to {level}')

    def heat_off(self) -> None:
        print('Heat off')


class MockHumidifier(Humidifier):
    """Mock humidifier"""

    def humidity_on(self, level=1):
        print(f'Setting humidifier to {level}')

    def humidity_off(self) -> None:
        print('Humidifier off')


class MockLight(Light):
    """Mock light"""

    def light_on(self, level=1):
        print(f'Setting light to {level}')

    def light_off(self) -> None:
        print('Light off')


class MockEnvironment(Environment):
    """Mock environment"""
    fan_class = MockFan

    def get_humidity(self) -> float:
        """Mock humidity varies from 0-100% on a sine wave over the course of 12 minutes"""
        second = (datetime.now().minute * 60) + datetime.now().second
        return generate_sine(0.5, 0.5, second, 720)

    def get_temp(self) -> float:
        """Mock temp varies from 60-80 degrees on a sine wave over the course of 5 minutes"""
        second = (datetime.now().minute * 60) + datetime.now().second
        return generate_sine(70, 10, second, 300)


def generate_sine(offset: float = 0,
                  sine_range: float = 1,
                  second: int = 0,
                  second_range: int = 60):
    """Return the point along an optionally-transformed sine wave for a given second"""
    return sine_range * math.sin((second / second_range) * 2 * math.pi) + offset
