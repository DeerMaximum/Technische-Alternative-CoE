"""Test the Technische Alternative CoE state observer."""
import asyncio
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import mock_state_change_event
from ta_cmi import CoE

from custom_components.ta_coe import TYPE_BINARY, TYPE_SENSOR, StateObserver
from custom_components.ta_coe.const import ANALOG_DOMAINS, DIGITAL_DOMAINS
from tests import STATE_AVAILABLE_PACKAGE

coe = CoE("")


@pytest.mark.asyncio
async def test_observer_receive_all_states_init(hass: HomeAssistant):
    """Test if the observer receives all states on init."""
    entity_list = ["sensor.test9", "binary_sensor.test"]

    with patch(STATE_AVAILABLE_PACKAGE) as get_states_mock:
        StateObserver(hass, coe, entity_list)

        assert len(get_states_mock.call_args_list) == len(entity_list)

        for entity_id in entity_list:
            matched = False
            for called_id in get_states_mock.call_args_list:
                if called_id.args[0] == entity_id:
                    matched = True

            assert matched


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_observer_update_handler_ignore_state(hass: HomeAssistant, state: str):
    """Test if the observer handles state changes states that are ignored."""

    entity_list = ["sensor.test"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value=None):
        observer = StateObserver(hass, coe, entity_list)
        new_state = State(entity_list[0], state)

        mock_state_change_event(hass, new_state)
        await hass.async_block_till_done()

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_observer_update_handler_ignore_state_init(
    hass: HomeAssistant, state: str
):
    """Test if the observer handles state changes states that are ignored on init."""
    entity_list = ["sensor.test"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value=state):
        observer = StateObserver(hass, coe, entity_list)

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_digital_state(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of digital entities."""
    entity_list = [domain + ".test"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value=None):
        observer = StateObserver(hass, coe, entity_list)
        new_state = State(entity_list[0], "on")

        mock_state_change_event(hass, new_state)
        await asyncio.sleep(0.1)

        assert len(observer._states[TYPE_BINARY]) == 1
        assert len(observer._states[TYPE_SENSOR]) == 0
        assert observer._states[TYPE_BINARY][entity_list[0]]


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_digital_state_init(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of digital entities on init."""
    entity_list = [domain + ".test2"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value="on") as get_mock:
        observer = StateObserver(hass, coe, entity_list)

        assert len(observer._states[TYPE_BINARY]) == 1
        assert len(observer._states[TYPE_SENSOR]) == 0
        assert observer._states[TYPE_BINARY][entity_list[0]]

        get_mock.assert_called_with(entity_list[0])


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_analog_state(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of analog entities."""
    entity_list = [domain + ".test2"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value=None):
        observer = StateObserver(hass, coe, entity_list)
        new_state = State(entity_list[0], "5.5")

        mock_state_change_event(hass, new_state)
        await asyncio.sleep(0.1)

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 1
        assert observer._states[TYPE_SENSOR][entity_list[0]]


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_analog_state_init(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of analog entities on init."""
    entity_list = [domain + ".test3"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value="5.5") as get_mock:
        observer = StateObserver(hass, coe, entity_list)

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 1
        assert observer._states[TYPE_SENSOR][entity_list[0]]

        get_mock.assert_called_with(entity_list[0])


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_same_state_analog(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states with analog same state."""
    entity_list = [domain + ".test3"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value="1"):
        observer = StateObserver(hass, coe, entity_list)
        new_state = State(entity_list[0], "1")

        observer._states[TYPE_SENSOR] = {entity_list[0]: "1"}

        mock_state_change_event(hass, new_state, new_state)
        await asyncio.sleep(0.1)

        # TODO Assert send value function not called


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_same_state_digital(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states with digital same state."""
    entity_list = [domain + ".test4"]

    with patch(STATE_AVAILABLE_PACKAGE, return_value="on"):
        observer = StateObserver(hass, coe, entity_list)
        new_state = State(entity_list[0], "on")

        observer._states[TYPE_BINARY] = {entity_list[0]: "on"}

        mock_state_change_event(hass, new_state, new_state)
        await asyncio.sleep(0.1)

        # TODO Assert send value function not called
