"""The Technische Alternative CoE integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ta_cmi import CoE

from .const import (
    _LOGGER,
    CONF_CAN_IDS,
    CONF_ENTITIES_TO_SEND,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    SCAN_INTERVAL,
    CONF_ANALOG_ENTITIES,
    CONF_DIGITAL_ENTITIES,
    FREE_SLOT_MARKER_ANALOG,
    FREE_SLOT_MARKER_DIGITAL,
    DIGITAL_DOMAINS,
    ANALOG_DOMAINS,
    ConfEntityToSend,
)
from .coordinator import CoEDataUpdateCoordinator
from .issues import check_coe_server_2x_issue
from .refresh_task import RefreshTask
from .state_observer import StateObserver
from .state_sender import StateSender
from .state_sender_v1 import StateSenderV1
from .state_sender_v2 import StateSenderV2
from .websocket import async_register_websocket_commands

PLATFORMS: list[str] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    check_coe_server_2x_issue(hass, entry)

    host: str = entry.data[CONF_HOST]

    update_interval: timedelta = SCAN_INTERVAL

    if entry.data.get(CONF_SCAN_INTERVAL, None) is not None:
        update_interval = timedelta(minutes=entry.data.get(CONF_SCAN_INTERVAL))

    coe = CoE(host, async_get_clientsession(hass))

    can_ids: list[int] = entry.data.get(CONF_CAN_IDS, [])

    coordinator = CoEDataUpdateCoordinator(hass, entry, coe, can_ids, update_interval)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await coordinator.async_config_entry_first_refresh()

    server_config = await coe.get_server_config()

    _LOGGER.debug(f"CoE server config: Version={server_config.coe_version}")

    sender: StateSender

    if server_config.coe_version == 1:
        sender = StateSenderV1(coe, entry.data.get(CONF_ENTITIES_TO_SEND, {}))
    else:
        sender = StateSenderV2(coe, entry.data.get(CONF_ENTITIES_TO_SEND, {}))

    observer = StateObserver(
        hass, coe, sender, entry.data.get(CONF_ENTITIES_TO_SEND, {})
    )

    task = RefreshTask(sender)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "observer": observer,
        "task": task,
    }

    async_register_websocket_commands(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if len(entry.data.get(CONF_ENTITIES_TO_SEND, {})) > 0:
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
        hass.config_entries.async_update_entry(entry, data=config)

    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate the config to the new format."""

    version = entry.version
    minor_version = entry.minor_version

    _LOGGER.debug("Migrating from version %s.%s", version, minor_version)
    if entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if minor_version > 1:
        return True

    new_sending_data: dict[str, Any] = {
        CONF_ANALOG_ENTITIES: [],
        CONF_DIGITAL_ENTITIES: [],
    }

    digital_id = 1
    analog_id = 1

    for entity_id in entry.data.get(CONF_ENTITIES_TO_SEND, {}).values():
        if entity_id == FREE_SLOT_MARKER_ANALOG:
            analog_id += 1
            continue
        elif entity_id == FREE_SLOT_MARKER_DIGITAL:
            digital_id += 1
            continue

        domain = entity_id.split(".")[0]
        if domain in DIGITAL_DOMAINS:
            new_sending_data[CONF_DIGITAL_ENTITIES].append(
                ConfEntityToSend(digital_id, entity_id)
            )
            digital_id += 1
        elif domain in ANALOG_DOMAINS:
            new_sending_data[CONF_ANALOG_ENTITIES].append(
                ConfEntityToSend(analog_id, entity_id)
            )
            analog_id += 1

    new_data = {**entry.data, CONF_ENTITIES_TO_SEND: new_sending_data}

    hass.config_entries.async_update_entry(
        entry,
        data=new_data,
        minor_version=2,
    )
    return True
