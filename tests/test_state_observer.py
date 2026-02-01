"""Test the Technische Alternative CoE state observer."""

import asyncio
from unittest.mock import patch

import pytest
from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import mock_state_change_event
from ta_cmi import CoE

from custom_components.ta_coe import StateObserver
from custom_components.ta_coe.const import (
    ANALOG_DOMAINS,
    CONF_ANALOG_ENTITIES,
    CONF_DIGITAL_ENTITIES,
    DIGITAL_DOMAINS,
    TYPE_BINARY,
    TYPE_SENSOR,
    ConfEntityToSend,
)
from tests import (
    StubStateSender,
)
from tests.const import STATE_AVAILABLE_PACKAGE, STATE_SENDER_UPDATE_DIGITAL_MANUEL_PACKAGE, \
    STATE_SENDER_UPDATE_ANALOG_MANUEL_PACKAGE, STATE_SENDER_STUB_UPDATE_DIGITAL_PACKAGE, \
    STATE_SENDER_STUB_UPDATE_ANALOG_PACKAGE, STATE_SENDER_STUB_UPDATE, STATE_SENDER_V1_UPDATE_DIGITAL_PACKAGE, \
    STATE_SENDER_V1_UPDATE_ANALOG_PACKAGE

coe = CoE("")
state_sender = StubStateSender(
    coe, {CONF_ANALOG_ENTITIES: [], CONF_DIGITAL_ENTITIES: []}
)


@pytest.mark.asyncio
async def test_observer_receive_all_states_all_states(hass: HomeAssistant):
    """Test if the observer receives all states on get all states."""
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, "sensor.test9")],
        CONF_DIGITAL_ENTITIES: [ConfEntityToSend(1, "binary_sensor.test")],
    }

    entity_ids = [
        x.entity_id
        for x in entity_list.get(CONF_ANALOG_ENTITIES, [])
        + entity_list.get(CONF_DIGITAL_ENTITIES, [])
    ]

    with (
        patch(STATE_AVAILABLE_PACKAGE) as get_states_mock,
        patch(
            STATE_SENDER_UPDATE_ANALOG_MANUEL_PACKAGE,
        ),
        patch(
            STATE_SENDER_UPDATE_DIGITAL_MANUEL_PACKAGE,
        ),
    ):
        await StateObserver(hass, coe, state_sender, entity_list).get_all_states()

        assert len(get_states_mock.call_args_list) == len(entity_list)

        for entity_id in entity_ids:
            matched = False
            for called_id in get_states_mock.call_args_list:
                if called_id.args[0] == entity_id:
                    matched = True

            assert matched


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_observer_update_handler_ignore_state(hass: HomeAssistant, state: str):
    """Test if the observer handles state changes states that are ignored."""

    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, "sensor.test")],
        CONF_DIGITAL_ENTITIES: [],
    }

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=None),
        patch(STATE_SENDER_V1_UPDATE_DIGITAL_PACKAGE) as digital_mock,
        patch(STATE_SENDER_V1_UPDATE_ANALOG_PACKAGE) as analog_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        new_state = State("sensor.test", state)

        mock_state_change_event(hass, new_state)
        await hass.async_block_till_done()

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 0

        analog_mock.assert_not_called()
        digital_mock.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_observer_update_handler_ignore_state_all_states(
    hass: HomeAssistant, state: str
):
    """Test if the observer handles state changes states that are ignored on get all states."""
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, "sensor.test")],
        CONF_DIGITAL_ENTITIES: [],
    }

    new_state = State("sensor.test", state)

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=new_state),
        patch(STATE_SENDER_STUB_UPDATE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        await observer.get_all_states()

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 0

        update_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_digital_state_on(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of digital entities when state is on."""

    entity_id = f"{domain}.test"
    entity_list = {
        CONF_ANALOG_ENTITIES: [],
        CONF_DIGITAL_ENTITIES: [ConfEntityToSend(1, entity_id)],
    }

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=None),
        patch(STATE_SENDER_STUB_UPDATE_DIGITAL_PACKAGE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        new_state = State(entity_id, "on")

        mock_state_change_event(hass, new_state)
        await asyncio.sleep(0.1)

        assert len(observer._states[TYPE_BINARY]) == 1
        assert len(observer._states[TYPE_SENSOR]) == 0
        assert observer._states[TYPE_BINARY][entity_id]

        update_mock.assert_called_once_with(entity_id, True)


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_digital_state_off(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of digital entities when state is off."""
    entity_id = f"{domain}.test"
    entity_list = {
        CONF_ANALOG_ENTITIES: [],
        CONF_DIGITAL_ENTITIES: [ConfEntityToSend(1, entity_id)],
    }

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=None),
        patch(STATE_SENDER_STUB_UPDATE_DIGITAL_PACKAGE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        new_state = State(entity_id, "off")

        mock_state_change_event(hass, new_state)
        await asyncio.sleep(0.1)

        assert len(observer._states[TYPE_BINARY]) == 1
        assert len(observer._states[TYPE_SENSOR]) == 0
        assert not observer._states[TYPE_BINARY][entity_id]

        update_mock.assert_called_once_with(entity_id, False)


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_digital_state_all_states(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of digital entities on get all states."""
    entity_id = f"{domain}.test2"
    entity_list = {
        CONF_ANALOG_ENTITIES: [],
        CONF_DIGITAL_ENTITIES: [ConfEntityToSend(1, entity_id)],
    }

    state = State(entity_id, "on")

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=state) as get_mock,
        patch(STATE_SENDER_UPDATE_DIGITAL_MANUEL_PACKAGE) as update_add_mock,
        patch(STATE_SENDER_STUB_UPDATE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        await observer.get_all_states()

        assert len(observer._states[TYPE_BINARY]) == 1
        assert len(observer._states[TYPE_SENSOR]) == 0
        assert observer._states[TYPE_BINARY][entity_id]

        get_mock.assert_called_with(entity_id)

        update_add_mock.assert_called_once_with(entity_id, True)
        update_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_analog_state(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of analog entities."""
    entity_id = f"{domain}.test2"
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, entity_id)],
        CONF_DIGITAL_ENTITIES: [],
    }

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=None),
        patch(STATE_SENDER_STUB_UPDATE_ANALOG_PACKAGE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        new_state = State(entity_id, "5.5", attributes={ATTR_UNIT_OF_MEASUREMENT: "°C"})

        mock_state_change_event(hass, new_state)
        await asyncio.sleep(0.1)

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 1
        assert observer._states[TYPE_SENSOR][entity_id]

        update_mock.assert_called_once_with(entity_id, 5.5, "°C")


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_analog_state_all_states(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states of analog entities on get all states."""
    entity_id = f"{domain}.test3"
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, entity_id)],
        CONF_DIGITAL_ENTITIES: [],
    }

    state = State(entity_id, "1", attributes={ATTR_UNIT_OF_MEASUREMENT: "°C"})

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=state) as get_mock,
        patch(STATE_SENDER_UPDATE_ANALOG_MANUEL_PACKAGE) as update_add_mock,
        patch(STATE_SENDER_STUB_UPDATE) as update_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        await observer.get_all_states()

        assert len(observer._states[TYPE_BINARY]) == 0
        assert len(observer._states[TYPE_SENSOR]) == 1
        assert observer._states[TYPE_SENSOR][entity_id]

        get_mock.assert_called_with(entity_id)

        update_add_mock.assert_called_once_with(entity_id, 1, "°C")
        update_mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ANALOG_DOMAINS)
async def test_observer_update_handler_update_same_state_analog(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states with analog same state."""
    entity_id = f"{domain}.test3"
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, entity_id)],
        CONF_DIGITAL_ENTITIES: [],
    }

    state = State(entity_id, "1")

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=state),
        patch(STATE_SENDER_UPDATE_ANALOG_MANUEL_PACKAGE) as sender_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)

        observer._states[TYPE_SENSOR] = {entity_id: "1"}

        mock_state_change_event(hass, state, state)
        await asyncio.sleep(0.1)

        sender_mock.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", DIGITAL_DOMAINS)
async def test_observer_update_handler_update_same_state_digital(
    hass: HomeAssistant, domain: str
):
    """Test if the observer handles state changes states with digital same state."""
    entity_id = f"{domain}.test4"
    entity_list = {
        CONF_ANALOG_ENTITIES: [ConfEntityToSend(1, entity_id)],
        CONF_DIGITAL_ENTITIES: [],
    }

    state = State(entity_id, "on")

    with (
        patch(STATE_AVAILABLE_PACKAGE, return_value=state),
        patch(STATE_SENDER_STUB_UPDATE_DIGITAL_PACKAGE) as sender_mock,
    ):
        observer = StateObserver(hass, coe, state_sender, entity_list)
        new_state = State(entity_id, "on")

        observer._states[TYPE_BINARY] = {entity_id: "on"}

        mock_state_change_event(hass, new_state, new_state)
        await asyncio.sleep(0.1)

        sender_mock.assert_not_called()
