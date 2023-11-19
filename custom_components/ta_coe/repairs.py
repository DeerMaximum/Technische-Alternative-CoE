"""Repairs for Technische Alternative CoE integration."""
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant

from custom_components.ta_coe import CONF_CAN_IDS
from custom_components.ta_coe.config_flow import CANIDError, split_can_ids


class MissingCANIDRepairFlow(RepairsFlow):
    """Handler for an missing CAN-ID fixing flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize."""
        self.config_entry = config_entry
        self.config_data = dict(self.config_entry.data)

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of a fix flow."""
        return await self.async_step_form()

    async def async_step_form(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of a fix flow."""

        errors: dict[str, Any] = {}

        if user_input is not None:
            try:
                self.config_data[CONF_CAN_IDS] = split_can_ids(user_input[CONF_CAN_IDS])
            except CANIDError:
                errors["base"] = "invalid_can_id"
            else:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=self.config_data
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="form",
            data_schema=vol.Schema({vol.Required(CONF_CAN_IDS): cv.string}),
            errors=errors,
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: Any | None,
) -> RepairsFlow:
    """Entry point for repair flows."""
    if issue_id == "add_missing_can_id":
        return MissingCANIDRepairFlow(hass.config_entries.async_get_entry(data))
