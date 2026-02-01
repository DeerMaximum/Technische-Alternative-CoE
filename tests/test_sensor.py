"""Test the Technische Alternative CoE sensor."""

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ta_coe.const import CONF_CAN_IDS
from tests import setup_platform
from tests.const import (
    DUMMY_CONFIG_ENTRY,
)


@pytest.mark.asyncio
async def test_sensors(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test the creation and values of the sensors."""

    await setup_platform(hass, mock_config_entry)

    entity_registry: er = er.async_get(hass)

    for can_id in DUMMY_CONFIG_ENTRY[CONF_CAN_IDS]:
        state_a1 = hass.states.get(f"sensor.coe_analog_can{can_id}_1")
        entry_a1 = entity_registry.async_get(f"sensor.coe_analog_can{can_id}_1")

        assert state_a1.state == "34.4"
        assert state_a1.attributes.get("friendly_name") == f"CoE Analog - CAN{can_id} 1"
        assert state_a1.attributes.get("device_class") == SensorDeviceClass.TEMPERATURE
        assert state_a1.attributes.get("state_class") == SensorStateClass.MEASUREMENT
        assert state_a1.attributes.get("unit_of_measurement") == "°C"

        assert entry_a1.unique_id == f"ta-coe-analog-can{can_id}-1"

        state_a2 = hass.states.get(f"sensor.coe_analog_can{can_id}_2")
        entry_a2 = entity_registry.async_get(f"sensor.coe_analog_can{can_id}_2")

        assert state_a2.state == "50.0"
        assert state_a2.attributes.get("friendly_name") == f"CoE Analog - CAN{can_id} 2"
        assert state_a2.attributes.get("device_class") == SensorDeviceClass.ENERGY
        assert state_a2.attributes.get("state_class") == SensorStateClass.TOTAL

        assert entry_a2.unique_id == f"ta-coe-analog-can{can_id}-2"

        state_a3 = hass.states.get(f"sensor.coe_analog_can{can_id}_3")
        entry_a3 = entity_registry.async_get(f"sensor.coe_analog_can{can_id}_3")

        assert state_a3.state == "60.0"
        assert state_a3.attributes.get("friendly_name") == f"CoE Analog - CAN{can_id} 3"
        assert state_a3.attributes.get("device_class") == SensorDeviceClass.ENERGY
        assert state_a3.attributes.get("state_class") == SensorStateClass.TOTAL

        assert entry_a3.unique_id == f"ta-coe-analog-can{can_id}-3"

        state_a4 = hass.states.get(f"sensor.coe_analog_can{can_id}_4")
        entry_a4 = entity_registry.async_get(f"sensor.coe_analog_can{can_id}_4")

        assert state_a4.state == "60.0"
        assert state_a4.attributes.get("friendly_name") == f"CoE Analog - CAN{can_id} 4"
        assert state_a4.attributes.get("device_class") == SensorDeviceClass.WATER
        assert state_a4.attributes.get("state_class") == SensorStateClass.TOTAL
        assert state_a4.attributes.get("unit_of_measurement") == "L"

        assert entry_a4.unique_id == f"ta-coe-analog-can{can_id}-4"

        state_d1 = hass.states.get(f"binary_sensor.coe_digital_can{can_id}_1")
        entry_d1 = entity_registry.async_get(f"binary_sensor.coe_digital_can{can_id}_1")

        assert state_d1.state == STATE_ON
        assert (
            state_d1.attributes.get("friendly_name") == f"CoE Digital - CAN{can_id} 1"
        )
        assert state_d1.attributes.get("device_class") is None

        assert entry_d1.unique_id == f"ta-coe-digital-can{can_id}-1"
