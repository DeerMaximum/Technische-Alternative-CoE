"""Test the Technische Alternative CoE state sender."""
from typing import Any
from unittest.mock import patch

import pytest
from ta_cmi import CoE, CoEChannel
from ta_cmi.const import ChannelMode

from custom_components.ta_coe import StateSender
from custom_components.ta_coe.const import ANALOG_DOMAINS, DIGITAL_DOMAINS
from custom_components.ta_coe.state_sender import AnalogValue
from tests import COE_SEND_ANALOG_VALUES_PACKAGE, COE_SEND_DIGITAL_VALUES_PACKAGE

coe = CoE("")


def create_dummy_ids(domain: str, count: int) -> dict[str, Any]:
    """Create dummy entity id dict."""
    dummy_data = {}

    for i in range(0, count):
        dummy_data[str(i)] = f"{domain}.{i}"

    return dummy_data


def test_sender_init_create_digital_pages():
    """When sender is initialized then empty digital states for all entities are created."""
    count = 8

    sender = StateSender(coe, create_dummy_ids(DIGITAL_DOMAINS[0], count))

    assert len(sender._digital_states) == count

    for i in range(0, count):
        assert sender._digital_states[str(i)] == False


def test_sender_init_create_analog_pages():
    """When sender is initialized then empty analog states for all entities are created."""
    count = 8

    sender = StateSender(coe, create_dummy_ids(ANALOG_DOMAINS[0], count))

    assert len(sender._analog_states) == count

    for i in range(0, count):
        assert sender._analog_states[str(i)] == AnalogValue(0, "0")


def test_sender_init_create_map_entity_id_to_index():
    """When sender is initialized then an entity id index mapping."""
    entity_ids = {
        "0": "sensor.1",
        "1": "binary_sensor.2",
        "2": "sensor.3",
        "3": "binary_sensor.4",
    }

    sender = StateSender(coe, entity_ids)

    assert sender._index_from_id == {
        entity_ids["0"]: "0",
        entity_ids["1"]: "0",
        entity_ids["2"]: "1",
        entity_ids["3"]: "1",
    }


def test_sender_digital_manuel_change_digital_page():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_ids(DIGITAL_DOMAINS[0], 8)
    sender = StateSender(coe, entities_ids)

    index_to_change = 1

    sender.update_digital_manuel(entities_ids[str(index_to_change)], True)

    for i in range(0, 8):
        assert sender._digital_states[str(i)] == (i == index_to_change)


def test_sender_analog_manuel_change_analog_page():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_ids(ANALOG_DOMAINS[0], 8)
    sender = StateSender(coe, entities_ids)

    index_to_change = 1

    value = AnalogValue(5.5, "°C")

    sender.update_analog_manuel(
        entities_ids[str(index_to_change)], value.value, value.unit
    )

    for i in range(0, 8):
        if i == index_to_change:
            assert sender._analog_states[str(i)] == value
        else:
            assert sender._analog_states[str(i)] == AnalogValue(0, "0")


@pytest.mark.asyncio
@pytest.mark.parametrize("page", range(1, 3))
async def test_sender_digital_change_digital_page(page: int):
    """Test when state added then the state on position is updated and changes are send to the server."""
    entities_ids = create_dummy_ids(DIGITAL_DOMAINS[0], 18)
    sender = StateSender(coe, entities_ids)

    index_to_change = 16 * (page - 1)

    with patch(COE_SEND_DIGITAL_VALUES_PACKAGE) as update_mock:
        await sender.update_digital(entities_ids[str(index_to_change)], True)

        expected = [CoEChannel(ChannelMode.DIGITAL, 16 * (page - 1), True, "")] + [
            CoEChannel(ChannelMode.DIGITAL, i + (16 * (page - 1)), False, "")
            for i in range(1, 16)
        ]

        update_mock.assert_called_once_with(expected, (page == 2))

        for i in range(0, 18):
            assert sender._digital_states[str(i)] == (i == index_to_change)


@pytest.mark.asyncio
@pytest.mark.parametrize("page", range(1, 9))
async def test_sender_analog_change_analog_page(page: int):
    """Test when state added then the state on position is updated and changes are send to the server."""
    entities_ids = create_dummy_ids(ANALOG_DOMAINS[0], 30)
    sender = StateSender(coe, entities_ids)

    index_to_change = 4 * (page - 1)

    with patch(COE_SEND_ANALOG_VALUES_PACKAGE) as update_mock:
        value = AnalogValue(5.5, "°C")

        await sender.update_analog(
            entities_ids[str(index_to_change)], value.value, value.unit
        )

        expected = [
            CoEChannel(ChannelMode.ANALOG, 4 * (page - 1), value.value, value.unit)
        ] + [
            CoEChannel(ChannelMode.ANALOG, i + (4 * (page - 1)), 0, "0")
            for i in range(1, 4)
        ]

        update_mock.assert_called_once_with(expected, page)

        for i in range(0, 30):
            if i == index_to_change:
                assert sender._analog_states[str(i)] == value
            else:
                assert sender._analog_states[str(i)] == AnalogValue(0, "0")


@pytest.mark.asyncio
async def test_sender_update_digital():
    """Test when updated all states are send to the server. Test with digital states."""
    entities_ids = create_dummy_ids(DIGITAL_DOMAINS[0], 30)
    sender = StateSender(coe, entities_ids)

    with patch(COE_SEND_DIGITAL_VALUES_PACKAGE) as update_mock, patch(
        COE_SEND_ANALOG_VALUES_PACKAGE
    ):
        await sender.update()

        sent_page = []
        sent_page_nr = []

        for calls in update_mock.call_args_list:
            sent_page += calls.args[0]
            sent_page_nr.append(calls.args[1])

        expected = [CoEChannel(ChannelMode.DIGITAL, i, False, "0") for i in range(32)]
        expected_page_nr = [False, True]

        assert len(expected) == len(sent_page)

        for i in range(len(expected)):
            assert expected[i].index == sent_page[i].index

        assert expected_page_nr == sent_page_nr


@pytest.mark.asyncio
async def test_sender_update_analog():
    """Test when updated all states are send to the server. Test with analog states."""
    entities_ids = create_dummy_ids(ANALOG_DOMAINS[0], 30)
    sender = StateSender(coe, entities_ids)

    with patch(COE_SEND_ANALOG_VALUES_PACKAGE) as update_mock, patch(
        COE_SEND_DIGITAL_VALUES_PACKAGE
    ):
        await sender.update()

        sent_page = []
        sent_page_nr = []

        for calls in update_mock.call_args_list:
            sent_page += calls.args[0]
            sent_page_nr.append(calls.args[1])

        expected = [CoEChannel(ChannelMode.ANALOG, i, 0, "0") for i in range(32)]
        expected_page_nr = [i for i in range(1, 9)]

        assert expected == sent_page

        assert expected_page_nr == sent_page_nr
