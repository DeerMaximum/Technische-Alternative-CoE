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
    CONF_ENTITIES_TO_SEND,
    CONF_SCAN_INTERVAL,
    CONF_SLOT_COUNT,
    DOMAIN,
    FREE_SLOT_MARKER,
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
                return await self.async_step_menu()

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

    async def async_step_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the menu step."""
        return self.async_show_menu(
            step_id="menu", menu_options=["send_values", "exit"]
        )

    async def async_step_send_values(self, user_input: dict[str, Any] | None = None):
        """Handle the configuration of sensors send via CoE."""

        errors: dict[str, Any] = {}

        if user_input is not None:
            new_id = user_input[CONF_ENTITIES_TO_SEND]
            if validate_entity(self.hass, new_id):
                if self._config.get(CONF_ENTITIES_TO_SEND, None) is None:
                    self._config[CONF_ENTITIES_TO_SEND] = {}

                if new_id not in self._config[CONF_ENTITIES_TO_SEND].values():
                    index = self._config.get(CONF_SLOT_COUNT, 0)

                    self._config[CONF_ENTITIES_TO_SEND][str(index)] = new_id
                    self._config[CONF_SLOT_COUNT] = index + 1

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
        self.config_entry = config_entry
        self.data = dict(self.config_entry.data)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "general",
                "add_send_values",
                "change_send_values",
                "delete_send_values",
            ],
        )

    async def async_step_add_send_values(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options add sensors send via CoE."""
        errors: dict[str, Any] = {}

        if user_input is not None:
            new_id = user_input[CONF_ENTITIES_TO_SEND]

            if validate_entity(self.hass, user_input[CONF_ENTITIES_TO_SEND]):
                if self.data.get(CONF_ENTITIES_TO_SEND, None) is None:
                    self.data[CONF_ENTITIES_TO_SEND] = {}

                if new_id not in self.data[CONF_ENTITIES_TO_SEND].values():
                    index = self.data.get(CONF_SLOT_COUNT, 0)

                    self.data[CONF_ENTITIES_TO_SEND][str(index)] = new_id
                    self.data[CONF_SLOT_COUNT] = index + 1

                    return self.async_create_entry(title="", data=self.data)

            errors["base"] = "invalid_entity"

        return self.async_show_form(
            step_id="add_send_values",
            data_schema=vol.Schema({vol.Required(CONF_ENTITIES_TO_SEND): cv.string}),
            errors=errors,
        )

    async def async_step_change_send_values(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options change sensors send via CoE."""
        errors: dict[str, Any] = {}

        if user_input is not None:
            new_id = user_input[CONF_ENTITIES_TO_SEND]
            old_id = user_input["old_value"]

            if (
                old_id in self.data[CONF_ENTITIES_TO_SEND].values()
                or new_id not in self.data[CONF_ENTITIES_TO_SEND].values()
            ) and old_id is not FREE_SLOT_MARKER:
                index = [
                    k
                    for k, v in self.data[CONF_ENTITIES_TO_SEND].items()
                    if v == old_id
                ][0]

                self.data[CONF_ENTITIES_TO_SEND][index] = new_id

                return self.async_create_entry(title="", data=self.data)

            errors["base"] = "invalid_entity"

        return self.async_show_form(
            step_id="change_send_values",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITIES_TO_SEND): cv.string,
                    vol.Required("old_value"): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_delete_send_values(self, user_input=None):
        """Handle options remove sensors send via CoE."""
        errors: dict[str, Any] = {}

        if user_input is not None:
            for index in user_input[CONF_ENTITIES_TO_SEND]:
                self.data[CONF_ENTITIES_TO_SEND][index] = FREE_SLOT_MARKER

            return self.async_create_entry(title="", data=self.data)

        entities_without_marker = {
            key: value
            for key, value in self.data.get(CONF_ENTITIES_TO_SEND, {}).items()
            if value != FREE_SLOT_MARKER
        }

        return self.async_show_form(
            step_id="delete_send_values",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITIES_TO_SEND): cv.multi_select(
                        entities_without_marker
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_general(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the general options."""

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
            step_id="general",
            data_schema=get_schema(self.data),
            errors=errors,
        )


class CANIDError(Exception):
    """Raised when invalid CAN-ID detected."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status
