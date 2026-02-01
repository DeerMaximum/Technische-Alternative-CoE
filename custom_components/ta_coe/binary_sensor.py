"""CoE binary sensor platform."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import CoEDataUpdateCoordinator
from .const import (
    DOMAIN,
    TYPE_BINARY,
)


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

    for can_id in coordinator.data.keys():
        for index, _ in coordinator.data[can_id][TYPE_BINARY].items():
            channel: DeviceChannelBinary = DeviceChannelBinary(
                coordinator, can_id, index
            )
            entities.append(channel)

    async_add_entities(entities)


class DeviceChannelBinary(CoordinatorEntity, BinarySensorEntity):
    """Representation of an CoE channel."""

    def __init__(
        self, coordinator: CoEDataUpdateCoordinator, can_id: int, channel_id: int
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._id = channel_id
        self._can_id = can_id
        self._coordinator = coordinator

        self._attr_name: str = f"CoE Digital - CAN{self._can_id} {self._id}"
        self._attr_unique_id: str = f"ta-coe-digital-can{self._can_id}-{self._id}"

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        channel_raw: dict[str, Any] = self._coordinator.data[self._can_id][TYPE_BINARY][
            self._id
        ]

        value: str = channel_raw["value"]

        return value in ("on", "yes")
