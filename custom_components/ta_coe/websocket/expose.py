"""Websocket commands for configuring exposed entities."""
from dataclasses import asdict
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from ..const import CONF_ANALOG_ENTITIES, CONF_ENTITIES_TO_SEND, CONF_DIGITAL_ENTITIES, ConfEntityToSend


@websocket_api.websocket_command({
    vol.Required("type"): "ta_coe/expose/info",
    vol.Required("config_entry_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def coe_exposed_entities_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return exposed entities configuration."""

    entry_id = msg["config_entry_id"]
    entry: ConfigEntry = hass.config_entries.async_get_entry(entry_id)

    entities_to_send = entry.data.get(CONF_ENTITIES_TO_SEND, {})

    connection.send_message(
        websocket_api.result_message(msg["id"], {"config": entities_to_send})
    )


@websocket_api.websocket_command({
    vol.Required("type"): "ta_coe/expose/update",
    vol.Required("config_entry_id"): str,
    vol.Required("config"): vol.Schema({
        vol.Required(CONF_ANALOG_ENTITIES): vol.All(
            cv.ensure_list,
            [
                vol.Schema({
                    vol.Required("id"): vol.All(vol.Coerce(int), vol.Range(min=1)),
                    vol.Required("entity_id"): cv.entity_id,
                })
            ],
        ),
        vol.Required(CONF_DIGITAL_ENTITIES): vol.All(
            cv.ensure_list,
            [
                vol.Schema({
                    vol.Required("id"): vol.All(vol.Coerce(int), vol.Range(min=1)),
                    vol.Required("entity_id"): cv.entity_id,
                })
            ],
        ),
    }),
})
@websocket_api.require_admin
@websocket_api.async_response
async def coe_exposed_entities_update(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Update exposed entities configuration."""

    entry_id = msg["config_entry_id"]
    entry: ConfigEntry = hass.config_entries.async_get_entry(entry_id)

    hass.config_entries.async_update_entry(
        entry, data={
            **entry.data,
            CONF_ENTITIES_TO_SEND: {
                CONF_ANALOG_ENTITIES: [asdict(ConfEntityToSend(**x)) for x in msg["config"][CONF_ANALOG_ENTITIES]],
                CONF_DIGITAL_ENTITIES: [asdict(ConfEntityToSend(**x)) for x in msg["config"][CONF_DIGITAL_ENTITIES]],
            }
        }
    )

    connection.send_message(
        websocket_api.result_message(msg["id"], {})
    )