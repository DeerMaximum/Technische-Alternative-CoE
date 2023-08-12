"""CoE sensor platform."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoEDataUpdateCoordinator
from .const import DEFAULT_DEVICE_CLASS_MAP, DOMAIN, TYPE_SENSOR


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entries."""
    coordinator: CoEDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    entities: list[DeviceChannelSensor] = []

    for index, _ in coordinator.data[TYPE_SENSOR].items():
        channel: DeviceChannelSensor = DeviceChannelSensor(coordinator, index)
        entities.append(channel)

    async_add_entities(entities)


class DeviceChannelSensor(CoordinatorEntity, SensorEntity):
    """Representation of an CoE channel."""

    def __init__(self, coordinator: CoEDataUpdateCoordinator, id: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._id = id
        self._coordinator = coordinator

        self._attr_name: str = f"CoE Analog - {self._id}"
        self._attr_unique_id: str = f"ta-coe-analog-{self._id}"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        channel_raw: dict[str, Any] = self._coordinator.data[TYPE_SENSOR][self._id]

        value: str = channel_raw["value"]

        return value

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""

        channel_raw: dict[str, Any] = self._coordinator.data[TYPE_SENSOR][self._id]

        unit: str = channel_raw["unit"]

        if unit == "l":
            return unit.upper()

        return unit

    @property
    def state_class(self) -> str:
        """Return the state class of the sensor."""
        if self.device_class in [SensorDeviceClass.ENERGY, SensorDeviceClass.WATER]:
            return SensorStateClass.TOTAL

        return SensorStateClass.MEASUREMENT

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class of this entity, if any."""
        channel_raw: dict[str, Any] = self._coordinator.data[TYPE_SENSOR][self._id]

        return DEFAULT_DEVICE_CLASS_MAP.get(channel_raw["unit"], None)
