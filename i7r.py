"""I7R Table implementations"""
from abc import abstractmethod
from sqlalchemy import Column, Date, DateTime, Numeric, String, ForeignKey, Time, select
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
# Make sure all subclasses of Base are in the `i7r` schema
setattr(Base, '__table_args__', {'schema': 'i7r'})


class Schedule(Base):
    """
    A schedule corresponds to a particular Environment.
    It declares what the ideal conditions should be, and when.
    """
    __tablename__ = 'schedules'
    id = Column(String, primary_key=True)
    name = Column(String)
    environment_id = Column(ForeignKey('i7r.environments.id'))
    start_at = Column(Time)
    end_at = Column(Time)
    start_date = Column(Date)
    end_date = Column(Date)
    light_level = Column(Numeric)
    temp = Column(Numeric)
    humidity = Column(Numeric)


class Reading(Base):
    """
    A Reading is a snapshot of the current state of a particular Environment.
    """
    __tablename__ = 'readings'

    id = Column(String, primary_key=True)
    environment_id = Column(ForeignKey('i7r.environments.id'))
    at = Column(DateTime)
    fan_id = Column(ForeignKey('i7r.fans.id'))
    fan_level = Column(Numeric)
    heater_id = Column(ForeignKey('i7r.heaters.id'))
    heater_level = Column(Numeric)
    humidifier_id = Column(ForeignKey('i7r.humidifiers.id'))
    humidity = Column(Numeric)
    light_id = Column(ForeignKey('i7r.lights.id'))
    light_level = Column(Numeric)
    temp = Column(Numeric)


class Fan(Base):
    """Fan"""
    __tablename__ = 'fans'

    id = Column(String, primary_key=True)
    name = Column(String)

    @abstractmethod
    def fan_on(self, level: float = 1) -> None:
        """Send a signal for the fan to engage."""

    @abstractmethod
    def fan_off(self) -> None:
        """Send a signal for the fan to disengage."""


class Humidifier(Base):
    """Humidifier"""
    __tablename__ = 'humidifiers'

    id = Column(String, primary_key=True)
    name = Column(String)

    @abstractmethod
    def humidity_on(self, level: float = 1) -> None:
        """Send a signal for the humidifier to engage."""

    @abstractmethod
    def humidity_off(self) -> None:
        """Send a signal for the humidifier to disengage."""


class Heater(Base):
    """Heater"""
    __tablename__ = 'heaters'

    id = Column(String, primary_key=True)
    name = Column(String)

    @abstractmethod
    def heat_on(self, level: float = 1) -> None:
        """Send a signal for the heater to engage."""

    @abstractmethod
    def heat_off(self) -> None:
        """Send a signal for the heater to disengage."""


class Light(Base):
    """Light"""
    __tablename__ = 'lights'

    id = Column(String, primary_key=True)
    name = Column(String)

    @abstractmethod
    def light_on(self, level: float = 1) -> None:
        """Send a signal for the light to engage."""

    @abstractmethod
    def light_off(self) -> None:
        """Send a signal for the light to disengage."""


class Environment(Base):
    """
    An environment represents an ecosystem that may include:
        - a light source
        - a heat source
        - a humidifier
        - a fan
    """
    __tablename__ = 'environments'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    name = Column(String)
    fan_id = Column(ForeignKey('i7r.fans.id'))
    heater_id = Column(ForeignKey('i7r.heaters.id'))
    humidifier_id = Column(ForeignKey('i7r.humidifiers.id'))
    light_id = Column(ForeignKey('i7r.lights.id'))
    humidity_default = Column(Numeric)
    temp_default = Column(Numeric)
    temp_tolerance = Column(Numeric)

    fan_class = Fan
    heater_class = Heater
    humidifier_class = Humidifier
    light_class = Light

    @abstractmethod
    def get_temp(self) -> float:
        """Get the current temperature in this environment."""

    @abstractmethod
    def get_humidity(self) -> float:
        """Get the current humidity in this environment."""

    def get_device(self, session: Session, device_type: str, device_id: str) -> Base:
        """Return the device of this type with this ID."""
        id_field = f'{device_type}_id'
        if not getattr(self, id_field, None):
            return None

        device_class = getattr(self, f'{device_type}_class')
        statement = select(device_class).where(
            device_class.id == device_id).limit(1)

        return session.execute(statement).scalars().one()

    def take_reading(self) -> None:
        """
        - Record the current environment conditions to the database.
        - Dispatch any events to controllers whose status should change
          based on the schedule and conditions.
        """
