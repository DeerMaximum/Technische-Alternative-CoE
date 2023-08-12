"""CoE binary sensor platform."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoEDataUpdateCoordinator
from .const import DOMAIN, TYPE_BINARY


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entries."""
    coordinator: CoEDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]

    entities: list[DeviceChannelBinary] = []

    for index, _ in coordinator.data[TYPE_BINARY].items():
        channel: DeviceChannelBinary = DeviceChannelBinary(coordinator, index)
        entities.append(channel)

    async_add_entities(entities)


class DeviceChannelBinary(CoordinatorEntity, BinarySensorEntity):
    """Representation of an CoE channel."""

    def __init__(self, coordinator: CoEDataUpdateCoordinator, channel_id: int) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._id = channel_id
        self._coordinator = coordinator

        self._attr_name: str = f"CoE Digital - {self._id}"
        self._attr_unique_id: str = f"ta-coe-digital-{self._id}"

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        channel_raw: dict[str, Any] = self._coordinator.data[TYPE_BINARY][self._id]

        value: str = channel_raw["value"]

        return value in ("on", "yes")
