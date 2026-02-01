"""Test the Technische Alternative CoE state sender V1."""

from unittest.mock import patch

import pytest
from ta_cmi import CoE, CoEChannel
from ta_cmi.const import ChannelMode

from custom_components.ta_coe import StateSenderV1
from custom_components.ta_coe.const import (
    ANALOG_DOMAINS,
    CONF_ANALOG_ENTITIES,
    CONF_DIGITAL_ENTITIES,
    DIGITAL_DOMAINS,
)
from custom_components.ta_coe.state_sender_v1 import AnalogValue
from tests import (
    create_dummy_conf_entity_to_send,
)
from tests.const import COE_SEND_ANALOG_VALUES_PACKAGE, COE_SEND_DIGITAL_VALUES_PACKAGE

coe = CoE("")


def test_sender_init_create_digital_pages():
    """When sender is initialized then empty digital states for all entities are created."""
    count = 8
    entities_ids = create_dummy_conf_entity_to_send(DIGITAL_DOMAINS[0], count)

    sender = StateSenderV1(coe, {CONF_DIGITAL_ENTITIES: entities_ids})

    assert len(sender._digital_states) == count

    for i in range(0, count):
        assert not sender._digital_states[str(i)]


def test_sender_init_create_analog_pages():
    """When sender is initialized then empty analog states for all entities are created."""
    count = 8
    entities_ids = create_dummy_conf_entity_to_send(ANALOG_DOMAINS[0], count)

    sender = StateSenderV1(coe, {CONF_ANALOG_ENTITIES: entities_ids})

    assert len(sender._analog_states) == count

    for i in range(0, count):
        assert sender._analog_states[str(i)] == AnalogValue(0, "0")


def test_sender_digital_manuel_change_digital_page():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_conf_entity_to_send(DIGITAL_DOMAINS[0], 8)
    sender = StateSenderV1(coe, {CONF_DIGITAL_ENTITIES: entities_ids})

    index_to_change = 1

    sender.update_digital_manuel(entities_ids[index_to_change].entity_id, True)

    for i in range(0, 8):
        assert sender._digital_states[str(i)] == (i == index_to_change)


def test_sender_analog_manuel_change_analog_page():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_conf_entity_to_send(ANALOG_DOMAINS[0], 8)
    sender = StateSenderV1(coe, {CONF_ANALOG_ENTITIES: entities_ids})

    index_to_change = 1

    value = AnalogValue(5.5, "°C")

    sender.update_analog_manuel(
        entities_ids[index_to_change].entity_id, value.value, value.unit
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
    entities_ids = create_dummy_conf_entity_to_send(DIGITAL_DOMAINS[0], 18)
    sender = StateSenderV1(coe, {CONF_DIGITAL_ENTITIES: entities_ids})

    index_to_change = 16 * (page - 1)

    with patch(COE_SEND_DIGITAL_VALUES_PACKAGE) as update_mock:
        await sender.update_digital(entities_ids[index_to_change].entity_id, True)

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
    entities_ids = create_dummy_conf_entity_to_send(ANALOG_DOMAINS[0], 30)
    sender = StateSenderV1(coe, {CONF_ANALOG_ENTITIES: entities_ids})

    index_to_change = 4 * (page - 1)

    with patch(COE_SEND_ANALOG_VALUES_PACKAGE) as update_mock:
        value = AnalogValue(5.5, "°C")

        await sender.update_analog(
            entities_ids[index_to_change].entity_id, value.value, value.unit
        )

        expected = [
            CoEChannel(ChannelMode.ANALOG, 4 * (page - 1), value.value, "46")
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
    entities_ids = create_dummy_conf_entity_to_send(DIGITAL_DOMAINS[0], 30)
    sender = StateSenderV1(coe, {CONF_DIGITAL_ENTITIES: entities_ids})

    with (
        patch(COE_SEND_DIGITAL_VALUES_PACKAGE) as update_mock,
        patch(COE_SEND_ANALOG_VALUES_PACKAGE),
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
    entities_ids = create_dummy_conf_entity_to_send(ANALOG_DOMAINS[0], 30)
    sender = StateSenderV1(coe, {CONF_ANALOG_ENTITIES: entities_ids})

    with (
        patch(COE_SEND_ANALOG_VALUES_PACKAGE) as update_mock,
        patch(COE_SEND_DIGITAL_VALUES_PACKAGE),
    ):
        await sender.update()

        sent_page = []
        sent_page_nr = []

        for calls in update_mock.call_args_list:
            sent_page += calls.args[0]
            sent_page_nr.append(calls.args[1])

        expected = [CoEChannel(ChannelMode.ANALOG, i, 0, "0") for i in range(32)]
        expected_page_nr = list(range(1, 9))

        assert expected == sent_page

        assert expected_page_nr == sent_page_nr
