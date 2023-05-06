"""Constants for the Technische Alternative CoE integration."""
from __future__ import annotations

from datetime import timedelta
from logging import Logger, getLogger

from homeassistant.components.sensor import SensorDeviceClass

_LOGGER: Logger = getLogger(__package__)

SCAN_INTERVAL: timedelta = timedelta(minutes=1)

DOMAIN: str = "ta_coe"

ADDON_HOSTNAME = "a824d5a9-ta-coe"
ADDON_DEFAULT_PORT = 9000

CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_DEVICE_CLASS_MAP: dict[str, SensorDeviceClass] = {
    "°C": SensorDeviceClass.TEMPERATURE,
    "K": SensorDeviceClass.TEMPERATURE,
    "A": SensorDeviceClass.CURRENT,
    "mA": SensorDeviceClass.CURRENT,
    "kWh": SensorDeviceClass.ENERGY,
    "MWh": SensorDeviceClass.ENERGY,
    "km/h": SensorDeviceClass.SPEED,
    "m/s": SensorDeviceClass.SPEED,
    "Hz": SensorDeviceClass.FREQUENCY,
    "km": SensorDeviceClass.DISTANCE,
    "m": SensorDeviceClass.DISTANCE,
    "mm": SensorDeviceClass.DISTANCE,
    "cm": SensorDeviceClass.DISTANCE,
    "%": SensorDeviceClass.HUMIDITY,
    "kg": SensorDeviceClass.WEIGHT,
    "t": SensorDeviceClass.WEIGHT,
    "g": SensorDeviceClass.WEIGHT,
    "lx": SensorDeviceClass.ILLUMINANCE,
    "W": SensorDeviceClass.POWER,
    "kW": SensorDeviceClass.POWER,
    "mbar": SensorDeviceClass.PRESSURE,
    "bar": SensorDeviceClass.PRESSURE,
    "Pa": SensorDeviceClass.PRESSURE,
    "V": SensorDeviceClass.VOLTAGE,
    "W/m²": SensorDeviceClass.IRRADIANCE,
}

TYPE_BINARY = "binary"
TYPE_SENSOR = "sensor"
