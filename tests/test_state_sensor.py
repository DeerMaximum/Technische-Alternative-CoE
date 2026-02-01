from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from ta_cmi import CoEServerConfig

from custom_components.ta_coe import CONF_ENTITIES_TO_SEND, DOMAIN
from custom_components.ta_coe.const import (
    ATTR_ANALOG_ORDER,
    ATTR_DIGITAL_ORDER,
    CONF_CAN_IDS,
)
from tests import setup_platform
from tests.const import COEAPI_PACKAGE, COE_SEND_ANALOG_VALUES_PACKAGE, COE_SEND_DIGITAL_VALUES_PACKAGE, \
    COE_CHECK_SERVER_VERSION_PACKAGE, OBSERVER_GET_ALL_STATES, REFRESH_TASK_START_PACKAGE, DUMMY_DEVICE_API_DATA

ENTRY_DATA_NO_SENDING: dict[str, Any] = {
    CONF_HOST: "http://192.168.2.101",
    CONF_CAN_IDS: [1, 20],
}

ENTITY_ID_STATE_SENSOR = "binary_sensor.coe_send_value_state"

server_config = CoEServerConfig(coe_version=2)


@pytest.mark.asyncio
async def test_state_sensor_off(hass: HomeAssistant) -> None:
    """Test the creation and values of the state sensors when no values are send."""
    with (
        patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA),
        patch(OBSERVER_GET_ALL_STATES) as observer_mock,
        patch(REFRESH_TASK_START_PACKAGE) as start_task_mock,
        patch(COE_CHECK_SERVER_VERSION_PACKAGE, return_value=server_config),
    ):
        conf_entry: MockConfigEntry = MockConfigEntry(
            domain=DOMAIN, title="CoE", data=ENTRY_DATA_NO_SENDING, minor_version=2
        )

        entity_registry: er = er.async_get(hass)
        conf_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(conf_entry.entry_id)
        await hass.async_block_till_done()

        assert conf_entry.state == ConfigEntryState.LOADED

        state_a1 = hass.states.get(ENTITY_ID_STATE_SENSOR)
        entry_a1 = entity_registry.async_get(ENTITY_ID_STATE_SENSOR)

        assert state_a1.state == STATE_OFF
        assert state_a1.attributes.get("friendly_name") == "CoE: Send value state"

        assert entry_a1.unique_id == "ta-coe-send-value-state"


@pytest.mark.asyncio
async def test_state_sensor_on(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test the creation and values of the state sensors when values are send.."""
    with (
        patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA),
        patch(COE_SEND_ANALOG_VALUES_PACKAGE),
        patch(COE_SEND_DIGITAL_VALUES_PACKAGE),
        patch(OBSERVER_GET_ALL_STATES) as observer_mock,
        patch(REFRESH_TASK_START_PACKAGE) as start_task_mock,
        patch(COE_CHECK_SERVER_VERSION_PACKAGE, return_value=server_config),
    ):
        entity_registry: er = er.async_get(hass)
        await setup_platform(hass, mock_config_entry)

        state_a1 = hass.states.get(ENTITY_ID_STATE_SENSOR)
        entry_a1 = entity_registry.async_get(ENTITY_ID_STATE_SENSOR)

        assert state_a1.state == STATE_ON
        assert state_a1.attributes.get("friendly_name") == "CoE: Send value state"
        # assert state_a1.attributes.get(ATTR_ANALOG_ORDER) == {
        #     2: ENTRY_DATA[CONF_ENTITIES_TO_SEND][3],
        # }
        # assert state_a1.attributes.get(ATTR_DIGITAL_ORDER) == {
        #     2: ENTRY_DATA[CONF_ENTITIES_TO_SEND][4],
        # }

        assert entry_a1.unique_id == "ta-coe-send-value-state"
