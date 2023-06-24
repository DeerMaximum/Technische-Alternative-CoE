"""Config flow for Technische Alternative CoE integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ta_cmi import ApiError, CoE

from .const import (
    _LOGGER,
    ADDON_DEFAULT_PORT,
    ADDON_HOSTNAME,
    ALLOWED_DOMAINS,
    CONF_ENTITIES_TO_SEND,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    SCAN_INTERVAL,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Technische Alternative CoE."""

    VERSION = 1

    override_data: dict[str, Any] = {}

    def __init__(self):
        self._config = self.override_data

    async def check_addon_available(self) -> bool:
        """Check if the CoE to HTTP addon is available."""
        coe: CoE = CoE(
            f"http://{ADDON_HOSTNAME}:{ADDON_DEFAULT_PORT}",
            async_get_clientsession(self.hass),
        )
        try:
            async with timeout(10):
                await coe.update()
        except (ApiError, asyncio.TimeoutError):
            return False
        else:
            return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, Any] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None and await self.check_addon_available():
            self._config = {CONF_HOST: f"http://{ADDON_HOSTNAME}:{ADDON_DEFAULT_PORT}"}
            return await self.async_step_menu()

        if user_input is not None:
            if not user_input[CONF_HOST].startswith("http://"):
                user_input[CONF_HOST] = "http://" + user_input[CONF_HOST]

            try:
                coe: CoE = CoE(
                    user_input[CONF_HOST], async_get_clientsession(self.hass)
                )
                async with timeout(10):
                    await coe.update()
            except (ApiError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                self._config = user_input
                return await self.async_step_menu()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): cv.string}),
            errors=errors,
        )

    async def async_step_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the menu step."""
        return self.async_show_menu(
            step_id="menu", menu_options=["send_values", "exit"]
        )

    def _validate_entity(self, entity_id: str) -> bool:
        """Validate an entity."""
        return entity_id.startswith(ALLOWED_DOMAINS) and self.hass.states.get(entity_id)

    async def async_step_send_values(self, user_input: dict[str, Any] | None = None):
        """Handle the configuration of sensors send via CoE."""

        errors: dict[str, Any] = {}

        if user_input is not None:
            if self._validate_entity(user_input[CONF_ENTITIES_TO_SEND]):
                if self._config.get(CONF_ENTITIES_TO_SEND, None) is None:
                    self._config[CONF_ENTITIES_TO_SEND] = []

                self._config[CONF_ENTITIES_TO_SEND].append(
                    user_input[CONF_ENTITIES_TO_SEND]
                )

                self._config[CONF_ENTITIES_TO_SEND] = list(
                    set(self._config[CONF_ENTITIES_TO_SEND])
                )

                if user_input["next"]:
                    return await self.async_step_send_values()

                return await self.async_step_exit()

            errors["base"] = "invalid_entity"

        return self.async_show_form(
            step_id="send_values",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITIES_TO_SEND): cv.string,
                    vol.Required("next"): cv.boolean,
                }
            ),
            errors=errors,
        )

    async def async_step_exit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Exit the flow and save."""
        return self.async_create_entry(title="CoE", data=self._config)

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
