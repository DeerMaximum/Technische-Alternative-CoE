from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from ta_cmi import CoE, CoEChannel, ChannelMode, ApiError

from .const import _LOGGER, DOMAIN, TYPE_SENSOR, TYPE_BINARY


class CoEDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching CoE data."""

    channel_count: dict[int, int] = {}

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        coe: CoE,
        can_ids: list[int],
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.config_entry = config_entry

        self.coe = coe
        self.can_ids = can_ids

        _LOGGER.debug("Used update interval: %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    @staticmethod
    def _format_input(target_channel: CoEChannel) -> tuple[str, str]:
        """Format the unit and value."""
        unit: str = target_channel.get_unit()
        value: str | float = target_channel.value

        if unit == "On/Off":
            unit = ""
            if bool(value):
                value = STATE_ON
            else:
                value = STATE_OFF

        if unit == "No/Yes":
            unit = ""
            if bool(value):
                value = "yes"
            else:
                value = "no"

        return value, unit

    @staticmethod
    def _get_type(mode: ChannelMode) -> str:
        """Get the data type."""
        if mode is ChannelMode.ANALOG:
            return TYPE_SENSOR

        return TYPE_BINARY

    async def _async_update_data(self) -> dict[int, Any]:
        """Update data."""
        try:
            return_data: dict[int, dict[str, Any]] = {}
            _LOGGER.debug("Try to update CoE")

            for can_id in self.can_ids:
                return_data[can_id] = {TYPE_BINARY: {}, TYPE_SENSOR: {}}

                await self.coe.update(can_id)

                for mode in ChannelMode:
                    for index, channel in self.coe.get_channels(can_id, mode).items():
                        value, unit = self._format_input(channel)
                        return_data[can_id][self._get_type(mode)][index] = {
                            "value": value,
                            "unit": unit,
                        }

            return return_data
        except ApiError as err:
            raise UpdateFailed(err) from err
