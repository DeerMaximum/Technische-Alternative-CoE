"""Websocket commands for configuring exposed entities."""
from typing import Any

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import voluptuous as vol

from ..const import CONF_ENTITIES_TO_SEND


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ta_coe/expose/info",
        vol.Required("config_entry_id"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def coe_exposed_entities_config(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Return exposed entities configuration."""

    entry_id = msg["config_entry_id"]
    entry: ConfigEntry = hass.config_entries.async_get_entry(entry_id)

    entities_to_send = entry.data.get(CONF_ENTITIES_TO_SEND, {})

    connection.send_message(websocket_api.result_message(msg['id'], {"config": entities_to_send}))