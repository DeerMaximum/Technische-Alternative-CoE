from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from ..const import DOMAIN


@websocket_api.websocket_command({
    vol.Required("type"): "ta_coe/config/list",
})
@websocket_api.require_admin
@websocket_api.async_response
async def coe_config_entries(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return all config entries ids and titles."""

    entries = hass.config_entries.async_entries(
        DOMAIN, include_disabled=False, include_ignore=False
    )

    response_data = [
        {
            "entry_id": entry.entry_id,
            "title": entry.title,
        }
        for entry in entries
    ]

    connection.send_message(
        websocket_api.result_message(msg["id"], {"entries": response_data})
    )
