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
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from ta_cmi import ApiError, CoE

from .const import (
    _LOGGER,
    ADDON_DEFAULT_PORT,
    ADDON_HOSTNAME,
    ALLOWED_DOMAINS,
    CONF_CAN_IDS,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    SCAN_INTERVAL,
)


def validate_entity(hass: HomeAssistant, entity_id: str) -> bool:
    """Validate an entity."""
    return entity_id.startswith(ALLOWED_DOMAINS) and hass.states.get(entity_id)


def split_can_ids(raw_ids: str) -> list[int]:
    """Split string to can ids."""
    string_ids = raw_ids.split(",")
    can_ids: list[int] = []

    for id_str in string_ids:
        if not id_str.strip().isdigit():
            raise CANIDError(id_str)

        parsed_id = int(id_str)

        if parsed_id <= 0 or parsed_id > 64:
            raise CANIDError(id_str)

        can_ids.append(parsed_id)

    return can_ids


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Technische Alternative CoE."""

    VERSION: int = 1
    MINOR_VERSION: int = 2

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
                await coe.update(1)
        except (ApiError, asyncio.TimeoutError):
            return False
        else:
            return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, Any] = {}

        if (
            user_input is None
            and await self.check_addon_available()
            and not self._async_current_entries()
        ):
            self._config = {CONF_HOST: f"http://{ADDON_HOSTNAME}:{ADDON_DEFAULT_PORT}"}

        if user_input is not None:
            if not user_input[CONF_HOST].startswith("http://"):
                user_input[CONF_HOST] = "http://" + user_input[CONF_HOST]

            try:
                user_input[CONF_CAN_IDS] = split_can_ids(user_input[CONF_CAN_IDS])

                coe: CoE = CoE(
                    user_input[CONF_HOST], async_get_clientsession(self.hass)
                )
                async with timeout(10):
                    await coe.get_server_version()
            except (ApiError, asyncio.TimeoutError):
                errors["base"] = "cannot_connect"
            except CANIDError:
                errors["base"] = "invalid_can_id"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                self._config = user_input
                return self.async_create_entry(title="CoE", data=self._config)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=self._config.get(CONF_HOST, "")
                    ): cv.string,
                    vol.Required(CONF_CAN_IDS): cv.string,
                }
            ),
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

    default_can_ids = ",".join(str(i) for i in config.get(CONF_CAN_IDS, []))

    return vol.Schema(
        {
            vol.Required(
                CONF_SCAN_INTERVAL, default=default_interval.seconds / 60
            ): vol.All(cv.positive_float, vol.Range(min=0.1, max=60.0)),
            vol.Required(CONF_CAN_IDS, default=default_can_ids): cv.string,
        }
    )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an option flow for Technische Alternative C.M.I.."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.data = dict(config_entry.data)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        errors: dict[str, Any] = {}

        if user_input is not None and not errors:
            self.data[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]

            try:
                self.data[CONF_CAN_IDS] = split_can_ids(user_input[CONF_CAN_IDS])
            except CANIDError:
                errors["base"] = "invalid_can_id"
            else:
                return self.async_create_entry(title="", data=self.data)

        return self.async_show_form(
            step_id="init",
            data_schema=get_schema(self.data),
            errors=errors,
        )


class CANIDError(Exception):
    """Raised when invalid CAN-ID detected."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
