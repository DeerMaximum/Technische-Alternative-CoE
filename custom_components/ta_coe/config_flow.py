"""Config flow for Technische Alternative CoE integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ta_cmi import ApiError, CoE

from .const import _LOGGER, CONF_SCAN_INTERVAL, DOMAIN, SCAN_INTERVAL


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Technische Alternative C.M.I.."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, Any] = {}

        if user_input is not None:
            if not user_input[CONF_HOST].startswith("http://"):
                user_input[CONF_HOST] = "http://" + user_input[CONF_HOST]

            try:
                coe: CoE = CoE(
                    user_input[CONF_HOST], async_get_clientsession(self.hass)
                )
                await coe.update()
            except ApiError:
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="CoE", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): cv.string}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


def get_schema(config: dict[str, Any]) -> vol.Schema:
    """Generate the schema."""

    default_interval: timedelta = SCAN_INTERVAL

    if config.get(CONF_SCAN_INTERVAL, None) is not None:
        default_interval = timedelta(minutes=config.get(CONF_SCAN_INTERVAL))

    return vol.Schema(
        {
            vol.Required(
                CONF_SCAN_INTERVAL, default=default_interval.seconds / 60
            ): vol.All(int, vol.Range(min=1, max=60)),
        }
    )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an option flow for Technische Alternative C.M.I.."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.data = dict(self.config_entry.data)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""

        errors: dict[str, Any] = {}

        if user_input is not None and not errors:
            self.data[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]

            return self.async_create_entry(title="", data=self.data)

        return self.async_show_form(
            step_id="init",
            data_schema=get_schema(self.data),
            errors=errors,
        )
