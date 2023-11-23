"""Issues for Technische Alternative CoE integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from custom_components.ta_coe import CONF_CAN_IDS

from .const import DOMAIN


def check_coe_server_2x_issue(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Check and create issues related to the CoE server 2.x upgrade."""

    if entry.data.get(CONF_CAN_IDS, None) is None:
        ir.async_create_issue(
            hass,
            DOMAIN,
            "add_missing_can_id",
            data=entry.entry_id,
            is_fixable=True,
            severity=ir.IssueSeverity.ERROR,
            translation_key="add_missing_can_id",
        )
