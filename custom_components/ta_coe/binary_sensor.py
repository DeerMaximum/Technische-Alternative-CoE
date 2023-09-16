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
    ANALOG_DOMAINS,
    ATTR_ANALOG_ORDER,
    ATTR_DIGITAL_ORDER,
    CONF_ENTITIES_TO_SEND,
    DIGITAL_DOMAINS,
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

    entities: list[DeviceChannelBinary | CoESendState] = []

    for index, _ in coordinator.data[TYPE_BINARY].items():
        channel: DeviceChannelBinary = DeviceChannelBinary(coordinator, index)
        entities.append(channel)

    entities.append(
        CoESendState(coordinator.config_entry.data.get(CONF_ENTITIES_TO_SEND, {}))
    )

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


class CoESendState(BinarySensorEntity):
    """Representation of the coe send values state."""

    def __init__(self, entities_to_send: dict[str, Any]) -> None:
        """Initialize."""
        self._entity = entities_to_send

        self._attr_name: str = "CoE: Send value state"
        self._attr_unique_id: str = "ta-coe-send-value-state"

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return len(self._entity) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes of the sensor."""
        if not self.is_on:
            return {}

        digital = {}
        analog = {}

        index = 1
        for x in self._entity.values():
            if x.split(".")[0] in DIGITAL_DOMAINS:
                digital[index] = x
                index += 1

        index = 1
        for x in self._entity.values():
            if x.split(".")[0] in ANALOG_DOMAINS:
                analog[index] = x
                index += 1

        return {ATTR_ANALOG_ORDER: analog, ATTR_DIGITAL_ORDER: digital}
