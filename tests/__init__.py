"""Tests for the Technische Alternative CoE integration."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from ta_cmi import CoE, CoEServerConfig

from custom_components.ta_coe import ConfEntityToSend
from custom_components.ta_coe.state_sender import StateSender
from tests.const import (
    COEAPI_PACKAGE,
    COE_CHECK_SERVER_VERSION_PACKAGE,
    COE_VERSION_CHECK_PACKAGE,
    DUMMY_DEVICE_API_DATA,
    OBSERVER_GET_ALL_STATES,
)


def create_dummy_conf_entity_to_send(domain: str, count: int) -> list[ConfEntityToSend]:
    """Create dummy entity id dict."""
    dummy_data = []

    for i in range(1, count + 1):
        dummy_data.append(ConfEntityToSend(i, f"{domain}.{i}"))

    return dummy_data


async def setup_single_platform(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    platform: Platform | None,
) -> None:
    """Set up a single NINA platform."""
    server_config = CoEServerConfig(coe_version=1)
    with (
        patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA),
        patch(OBSERVER_GET_ALL_STATES),
        patch(COE_VERSION_CHECK_PACKAGE, return_value=None),
        patch(COE_CHECK_SERVER_VERSION_PACKAGE, return_value=server_config),
    ):
        platforms = [platform] if platform else []

        with patch("custom_components.ta_coe.PLATFORMS", platforms):
            assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        assert config_entry.state is ConfigEntryState.LOADED


async def setup_platform(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Set up the platform."""
    server_config = CoEServerConfig(coe_version=1)
    with (
        patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA),
        patch(OBSERVER_GET_ALL_STATES),
        patch(COE_VERSION_CHECK_PACKAGE, return_value=None),
        patch(COE_CHECK_SERVER_VERSION_PACKAGE, return_value=server_config),
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        assert config_entry.state is ConfigEntryState.LOADED


class StubStateSender(StateSender):
    def __init__(
        self, coe_intern: CoE, entity_config: dict[str, list[ConfEntityToSend]]
    ):
        super().__init__(coe_intern, entity_config)

    async def update_digital(self, entity_id: str, state: bool) -> None:
        """Update a digital state with sending update."""
        pass

    async def update_analog(self, entity_id: str, state: float, unit: str) -> None:
        """Update an analog state with sending update."""
        pass

    async def update(self) -> None:
        """Send all values to the server."""
        pass
