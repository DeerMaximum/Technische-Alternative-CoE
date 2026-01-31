"""Custom websocket handlers for the Technische Alternative CoE integration."""

from homeassistant.core import HomeAssistant, callback
from homeassistant.components import websocket_api

from .send import coe_exposed_entities_config


@callback
def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register CoE-specific websocket commands."""
    websocket_api.async_register_command(hass, coe_exposed_entities_config)

