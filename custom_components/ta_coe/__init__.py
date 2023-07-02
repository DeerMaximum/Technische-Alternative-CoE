"""The Technische Alternative CoE integration."""
from __future__ import annotations

from datetime import timedelta
from types import MappingProxyType
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from ta_cmi import ApiError, ChannelMode, CoE, CoEChannel

from .const import (
    _LOGGER,
    CONF_ENTITIES_TO_SEND,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    SCAN_INTERVAL,
    TYPE_BINARY,
    TYPE_SENSOR,
)
from .refresh_task import RefreshTask
from .state_observer import StateObserver
from .state_sender import StateSender

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""
    host: str = entry.data[CONF_HOST]

    update_interval: timedelta = SCAN_INTERVAL

    if entry.data.get(CONF_SCAN_INTERVAL, None) is not None:
        update_interval = timedelta(minutes=entry.data.get(CONF_SCAN_INTERVAL))

    coe = CoE(host, async_get_clientsession(hass))

    coordinator = CoEDataUpdateCoordinator(hass, entry, coe, update_interval)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await coordinator.async_config_entry_first_refresh()

    sender = StateSender(coe, entry.data.get(CONF_ENTITIES_TO_SEND, {}))
    observer = StateObserver(
        hass, coe, sender, entry.data.get(CONF_ENTITIES_TO_SEND, {})
    )

    task = RefreshTask(sender)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "observer": observer,
        "task": task,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await observer.get_all_states()

    await task.start()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    task: RefreshTask = hass.data[DOMAIN][entry.entry_id]["task"]

    await task.stop()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    config = dict(entry.data)
    if entry.options:
        config.update(entry.options)
        entry.data = MappingProxyType(config)

    await hass.config_entries.async_reload(entry.entry_id)


class CoEDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching CoE data."""

    channel_count = 0

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        coe: CoE,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.config_entry = config_entry

        self.coe = coe

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

    async def _check_new_channel(self, new_data: dict[str, Any]) -> None:
        """Check and reload if a new channel exists."""
        new_channel_count = len(new_data[TYPE_BINARY]) + len(new_data[TYPE_SENSOR])

        if self.channel_count != new_channel_count and self.channel_count != 0:
            _LOGGER.debug("New channels detected. Reload integration.")
            await self.hass.async_add_job(
                self.hass.config_entries.async_reload(self.config_entry.entry_id)
            )

        self.channel_count = new_channel_count

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data."""
        try:
            return_data: dict[str, Any] = {TYPE_BINARY: {}, TYPE_SENSOR: {}}

            _LOGGER.debug("Try to update CoE")

            await self.coe.update()

            for mode in ChannelMode:
                for index, channel in self.coe.get_channels(mode).items():
                    value, unit = self._format_input(channel)
                    return_data[self._get_type(mode)][index] = {
                        "value": value,
                        "unit": unit,
                    }

            await self._check_new_channel(return_data)

            return return_data
        except ApiError as err:
            raise UpdateFailed(err) from err
