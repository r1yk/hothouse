"""Mock implementations of hothouse environment + devices"""

from datetime import datetime
import math
from hothouse import Environment, Device


class MockFan(Device):
    """Mock fan"""

    def _on(self, level):
        print(f'Setting fan to {level}')

    def _off(self) -> None:
        print('fan off')


class MockHeater(Device):
    """Mock heater"""

    def _on(self, level):
        print(f'Setting heat to {level}')

    def _off(self) -> None:
        print('Heat off')


class MockHumidifier(Device):
    """Mock humidifier"""

    def _on(self, level):
        print(f'Setting humidifier to {level}')

    def _off(self) -> None:
        print('Humidifier off')


class MockLight(Device):
    """Mock light"""

    def _on(self, level):
        print(f'Setting light to {level}')

    def _off(self) -> None:
        print('Light off')


class MockEnvironment(Environment):
    """Mock environment"""
    fan_class = MockFan
    light_class = MockLight
    heater_class = MockHeater
    humidifier_class = MockHumidifier

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
