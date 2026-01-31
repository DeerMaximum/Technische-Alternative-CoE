from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from ta_cmi import CoEServerConfig

from custom_components.ta_coe import DOMAIN, CONF_CAN_IDS, CONF_ENTITIES_TO_SEND, FREE_SLOT_MARKER_ANALOG, \
    FREE_SLOT_MARKER_DIGITAL, CONF_ANALOG_ENTITIES, CONF_DIGITAL_ENTITIES, ConfEntityToSend
from tests import COEAPI_PACKAGE, DUMMY_DEVICE_API_DATA, OBSERVER_GET_ALL_STATES, REFRESH_TASK_START_PACKAGE, \
    COE_CHECK_SERVER_VERSION_PACKAGE, COE_VERSION_CHECK_PACKAGE

server_config = CoEServerConfig(coe_version=2)

ENTRY_DATA: dict[str, Any] = {
    CONF_HOST: "http://192.168.2.101",
    CONF_CAN_IDS: [1, 20],
    CONF_ENTITIES_TO_SEND: {
        CONF_ANALOG_ENTITIES: [
            ConfEntityToSend(2, "sensor.coe_analog_2")
        ],
        CONF_DIGITAL_ENTITIES: [
            ConfEntityToSend(2, "binary_sensor.coe_digital_2")
        ]
    }
}

@pytest.mark.asyncio
async def test_config_migration_from1_1(
    hass: HomeAssistant
) -> None:
    """Test the migration to a new configuration layout."""

    with patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA), patch(
            OBSERVER_GET_ALL_STATES
    ), patch(REFRESH_TASK_START_PACKAGE), patch(
        COE_VERSION_CHECK_PACKAGE, return_value=None
    ), patch(
        COE_CHECK_SERVER_VERSION_PACKAGE, return_value=server_config
    ):
        old_entry : dict[str, Any] = {
            CONF_HOST: "http://192.168.2.101",
            CONF_CAN_IDS: [1, 20],
            CONF_ENTITIES_TO_SEND: {
                1: FREE_SLOT_MARKER_ANALOG,
                2: FREE_SLOT_MARKER_DIGITAL,
                3: "sensor.coe_analog_2",
                4: "binary_sensor.coe_digital_2",
            },
        }

        conf_entry: MockConfigEntry = MockConfigEntry(
            domain=DOMAIN, title="CoE", data=old_entry, minor_version=1, version=1
        )

        conf_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(conf_entry.entry_id)
        await hass.async_block_till_done()

        assert dict(conf_entry.data) == ENTRY_DATA
        assert conf_entry.state is ConfigEntryState.LOADED
        assert conf_entry.version == 1
        assert conf_entry.minor_version == 2

async def test_config_migration_downgrade(
    hass: HomeAssistant,
) -> None:
    """Test the migration to an old version."""

    conf_entry: MockConfigEntry = MockConfigEntry(
        domain=DOMAIN, title="CoE", data=ENTRY_DATA, version=2
    )

    conf_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(conf_entry.entry_id)
    await hass.async_block_till_done()

    assert dict(conf_entry.data) == ENTRY_DATA
    assert conf_entry.state is ConfigEntryState.MIGRATION_ERROR