"""Constants for the Technische Alternative CoE integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from logging import Logger, getLogger

from homeassistant.components.sensor import SensorDeviceClass

_LOGGER: Logger = getLogger(__package__)

SCAN_INTERVAL: timedelta = timedelta(minutes=1)

DOMAIN: str = "ta_coe"

ADDON_HOSTNAME = "a824d5a9-ta-coe"
ADDON_DEFAULT_PORT = 9000

CONF_CAN_IDS = "can_ids"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENTITIES_TO_SEND = "entities_to_send"
CONF_SLOT_COUNT = "slot_count"
CONF_ANALOG_ENTITIES = "analog"
CONF_DIGITAL_ENTITIES = "digital"

FREE_SLOT_MARKER_ANALOG = "--FREE_SLOT_MARKER_A--"
FREE_SLOT_MARKER_DIGITAL = "--FREE_SLOT_MARKER_D--"
FREE_SLOT_MARKERS = [FREE_SLOT_MARKER_ANALOG, FREE_SLOT_MARKER_DIGITAL]


@dataclass(frozen=True)
class ConfEntityToSend:
    id: int
    entity_id: str


DIGITAL_DOMAINS = ["binary_sensor", "input_boolean"]
ANALOG_DOMAINS = ["sensor", "number", "input_number"]
ALLOWED_DOMAINS = tuple(DIGITAL_DOMAINS + ANALOG_DOMAINS)

ATTR_ANALOG_ORDER = "analog_order"
ATTR_DIGITAL_ORDER = "digital_order"

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
    "l": SensorDeviceClass.WATER,
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
