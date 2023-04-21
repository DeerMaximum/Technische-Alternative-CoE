"""Test the Technische Alternative CoE sensor."""
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ta_coe.const import DOMAIN
from tests import COEAPI_PACKAGE

DUMMY_DEVICE_API_DATA: dict[str, Any] = {
    "digital": [{"value": True, "unit": 43}],
    "analog": [{"value": 34.4, "unit": 1}],
    "last_update_unix": 1680410064.03764,
    "last_update": "2023-04-01T12:00:00",
}

ENTRY_DATA: dict[str, Any] = {"host": "http://192.168.2.101"}


@pytest.mark.asyncio
async def test_sensors(hass: HomeAssistant) -> None:
    """Test the creation and values of the sensors."""
    with patch(COEAPI_PACKAGE, return_value=DUMMY_DEVICE_API_DATA):
        conf_entry: MockConfigEntry = MockConfigEntry(
            domain=DOMAIN, title="CoE", data=ENTRY_DATA
        )

        entity_registry: er = er.async_get(hass)
        conf_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(conf_entry.entry_id)
        await hass.async_block_till_done()

        assert conf_entry.state == ConfigEntryState.LOADED

        state_a1 = hass.states.get("sensor.coe_analog_1")
        entry_a1 = entity_registry.async_get("sensor.coe_analog_1")

        assert state_a1.state == "34.4"
        assert state_a1.attributes.get("friendly_name") == "CoE Analog - 1"
        assert state_a1.attributes.get("device_class") == SensorDeviceClass.TEMPERATURE

        assert entry_a1.unique_id == "ta-coe-analog-1"

        state_d2 = hass.states.get("binary_sensor.coe_digital_1")
        entry_d2 = entity_registry.async_get("binary_sensor.coe_digital_1")

        assert state_d2.state == STATE_ON
        assert state_d2.attributes.get("friendly_name") == "CoE Digital - 1"
        assert state_d2.attributes.get("device_class") is None

        assert entry_d2.unique_id == "ta-coe-digital-1"
