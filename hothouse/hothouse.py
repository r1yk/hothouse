"""Hothouse Table implementations"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, ForeignKey, Time, or_, select
from sqlalchemy.orm import declarative_base, Session
from hothouse.postgres import get_session

Base = declarative_base()
# Make sure all subclasses of Base are in the `hothouse` schema
setattr(Base, '__table_args__', {'schema': 'hh'})


class Schedule(Base):
    """
    A schedule corresponds to a particular Environment.
    It declares what the ideal conditions should be, and when.
    """
    __tablename__ = 'schedules'
    id = Column(String, primary_key=True)
    environment_id = Column(ForeignKey('hh.devices.id'))
    end_date = Column(Date)
    fan_on_seconds = Column(Integer)
    fan_off_seconds = Column(Integer)
    start_date = Column(Date)
    light_on_at = Column(Time)
    light_off_at = Column(Time)
    temp = Column(Numeric)
    humidity = Column(Numeric)


class Reading(Base):
    """
    A Reading is a snapshot of the current state of a particular Environment.
    """
    __tablename__ = 'readings'

    id = Column(String, primary_key=True)
    environment_id = Column(ForeignKey('hh.devices.id'))
    at = Column(DateTime)
    fan_id = Column(ForeignKey('hh.devices.id'))
    fan_active = Column(Boolean)
    heater_id = Column(ForeignKey('hh.devices.id'))
    heater_active = Column(Boolean)
    humidifier_id = Column(ForeignKey('hh.devices.id'))
    humidifier_active = Column(Boolean)
    humidity = Column(Numeric)
    light_id = Column(ForeignKey('hh.devices.id'))
    light_active = Column(Boolean)
    temp = Column(Numeric)


class Device(Base):
    __tablename__ = 'devices'
    id = Column(String, primary_key=True)
    name = Column(String)
    active = Column(Boolean)
    voltage = Column(Numeric)
    watts = Column(Numeric)
    last_activated_at = Column(DateTime)

    def on(self, level: float = 1) -> None:
        """Send a signal for the device to engage."""
        self.active = True
        self.last_activated_at = datetime.now()
        self._on(level)

    def _on(self) -> None:
        pass

    def off(self) -> None:
        """Send a signal for the device to disengage."""
        self.active = False
        self._off()
        self._record_usage()

    def _off(self) -> None:
        pass

    def _record_usage() -> None:
        pass


class DeviceUsages(Base):
    __tablename__ = 'device_usages'
    id = Column(String, primary_key=True)
    device_id = Column(ForeignKey('hh.devices.id'))
    environment_id = Column(ForeignKey('hh.environments.id'))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    seconds = Column(Integer)
    kilowatt_hours = Column(Numeric)


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
    fan_id = Column(ForeignKey('hh.devices.id'))
    heater_id = Column(ForeignKey('hh.devices.id'))
    humidifier_id = Column(ForeignKey('hh.devices.id'))
    light_id = Column(ForeignKey('hh.devices.id'))
    humidity_default = Column(Numeric)
    humidity_tolerance = Column(Numeric)
    temp_default = Column(Numeric)
    temp_tolerance = Column(Numeric)

    # Override these static attributes for subclasses of `Environment`
    fan_class = Device
    heater_class = Device
    humidifier_class = Device
    light_class = Device

    def get_temp(self) -> float:
        """Get the current temperature in this environment."""

    def get_humidity(self) -> float:
        """Get the current humidity in this environment."""

    def take_reading(self, at: datetime = None) -> None:
        """
        - Record the current environment conditions to the database.
        - Dispatch any events to controllers whose status should change
          based on the schedule and conditions.
        """
        now = at or datetime.now()
        humidity = self.get_humidity()
        temp = self.get_temp()

        session: Session
        with get_session() as session:
            schedule_query = select(Schedule).where(
                Schedule.environment_id == self.id,
                Schedule.start_date < now,
                or_(Schedule.end_date == None, Schedule.end_date > now)
            )

            schedule = session.execute(schedule_query).scalars().one_or_none()
            if schedule is not None:
                fan: Device = session.get(self.fan_class, self.fan_id)
                heater: Device = session.get(self.heater_class, self.heater_id)
                humidifier: Device = session.get(
                    self.humidifier_class, self.humidifier_id)
                light: Device = session.get(self.light_class, self.light_id)

                # Temp control
                if heater is not None:
                    temp_target = float(
                        schedule.temp or self.temp_default or 70)
                    temp_tolerance = float(self.temp_tolerance or 3)

                    # Check if the current temperature below the allowable tolerance
                    if not heater.active and (temp_target - temp_tolerance > temp):
                        heater.active = True
                        heater.on()

                    # Check if the current temperature above the allowable tolerance
                    elif heater.active and (temp - temp_tolerance > temp_target):
                        heater.active = False
                        heater.off()

                # Humidity control
                if humidifier is not None:
                    humidity_target = float(
                        schedule.humidity or self.humidity_default or 0.5)
                    humidity_tolerance = float(self.humidity_tolerance or 0.1)

                    # Check if the current humidity below the allowable tolerance
                    if not humidifier.active and (humidity_target - humidity_tolerance > humidity):
                        humidifier.active = True
                        humidifier.on()

                    # Check if the current humidity above the allowable tolerance
                    elif humidifier.active and (humidity - humidity_tolerance > humidity_target):
                        humidifier.active = False
                        humidifier.off()

                # Fan control
                if fan is not None:
                    if schedule.fan_on_seconds and schedule.fan_off_seconds:
                        this_second = (now.hour * 60 * 60) + \
                            (now.minute * 60) + now.second
                        fan_total_period = schedule.fan_on_seconds + schedule.fan_off_seconds

                        # Check if the current second falls within the period when the fan should be on
                        during_fan_on = this_second % fan_total_period < schedule.fan_on_seconds
                        if not fan.active and during_fan_on:
                            fan.active = True
                            fan.on()

                        elif fan.active and not during_fan_on:
                            fan.active = False
                            fan.off()

                # Light control
                if light is not None and schedule.light_on_at and schedule.light_off_at:
                    now_time = now.time()
                    during_light_on = now_time > schedule.light_on_at and now_time < schedule.light_off_at
                    if not light.active and during_light_on:
                        light.active = True
                        light.on()

                    elif light.active and not during_light_on:
                        light.active = False
                        light.off()

                reading = Reading(
                    id=str(uuid4()),
                    at=now,
                    environment_id=self.id,
                    fan_id=self.fan_id,
                    fan_active=fan and fan.active or False,
                    heater_id=self.heater_id,
                    heater_active=heater and heater.active or False,
                    light_id=self.light_id,
                    light_active=light and light.active or False,
                    humidifier_id=self.humidifier_id,
                    humidifier_active=humidifier and humidifier.active or False,
                    humidity=humidity,
                    temp=temp
                )

                session.add(reading)
                session.commit()
