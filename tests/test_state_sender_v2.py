"""Test the Technische Alternative CoE state sender V2."""
from unittest.mock import patch

import pytest
from ta_cmi import ChannelMode, CoE, CoEChannel

from custom_components.ta_coe.const import ANALOG_DOMAINS, DIGITAL_DOMAINS
from custom_components.ta_coe.state_sender import AnalogValue
from custom_components.ta_coe.state_sender_v2 import StateSenderV2
from tests import (
    COE_SEND_ANALOG_VALUES_V2_PACKAGE,
    COE_SEND_DIGITAL_VALUES_V2_PACKAGE,
    STATE_SENDER_V2_UPDATE_ANALOG_MANUEL_PACKAGE,
    STATE_SENDER_V2_UPDATE_DIGITAL_MANUEL_PACKAGE,
    create_dummy_ids,
)

coe = CoE("")


def test_sender_digital_manuel_change_digital_state():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_ids(DIGITAL_DOMAINS[0], 8)
    sender = StateSenderV2(coe, entities_ids)

    index_to_change = 1

    sender.update_digital_manuel(entities_ids[str(index_to_change)], True)

    for i in range(0, 8):
        if i == index_to_change:
            assert sender._digital_states[str(i)]
        else:
            assert sender._digital_states.get(str(i)) is None


def test_sender_analog_manuel_change_analog_state():
    """Test when state manuel added then the state on position is updated."""
    entities_ids = create_dummy_ids(ANALOG_DOMAINS[0], 8)
    sender = StateSenderV2(coe, entities_ids)

    index_to_change = 1

    value = AnalogValue(5.5, "°C")

    sender.update_analog_manuel(
        entities_ids[str(index_to_change)], value.value, value.unit
    )

    for i in range(0, 8):
        if i == index_to_change:
            assert sender._analog_states[str(i)] == value
        else:
            assert sender._digital_states.get(str(i)) is None


@pytest.mark.asyncio
async def test_sender_update_digital():
    """Test the update_digital function."""
    entities_ids = {"0": "binary_sensor.test0"}
    sender = StateSenderV2(coe, entities_ids)

    with patch(COE_SEND_DIGITAL_VALUES_V2_PACKAGE) as update_mock, patch(
        STATE_SENDER_V2_UPDATE_DIGITAL_MANUEL_PACKAGE
    ) as update_manual_mock:
        await sender.update_digital(entities_ids["0"], True)

        expected = CoEChannel(ChannelMode.DIGITAL, 1, True, "43")

        update_mock.assert_called_once_with([expected])
        update_manual_mock.assert_called_once_with(entities_ids["0"], True)


@pytest.mark.asyncio
async def test_sender_update_analog():
    """Test the update_analog function."""
    entities_ids = {"0": "sensor.test0"}
    sender = StateSenderV2(coe, entities_ids)

    with patch(COE_SEND_ANALOG_VALUES_V2_PACKAGE) as update_mock, patch(
        STATE_SENDER_V2_UPDATE_ANALOG_MANUEL_PACKAGE
    ) as update_manual_mock:
        await sender.update_analog(entities_ids["0"], 43.2, "kW")

        expected = CoEChannel(ChannelMode.ANALOG, 1, 43.2, "10")

        update_mock.assert_called_once_with([expected])
        update_manual_mock.assert_called_once_with(entities_ids["0"], 43.2, "kW")


@pytest.mark.asyncio
async def test_sender_update_test_digital():
    """Test when updated all states are send to the server. Test with digital states."""
    entities_ids = create_dummy_ids(DIGITAL_DOMAINS[0], 30)
    sender = StateSenderV2(coe, entities_ids)

    with patch(COE_SEND_DIGITAL_VALUES_V2_PACKAGE) as update_mock, patch(
        COE_SEND_ANALOG_VALUES_V2_PACKAGE
    ):
        for i in range(30):
            sender.update_digital_manuel(entities_ids[str(i)], (i % 2 == 1))

        await sender.update()

        expected = [
            CoEChannel(ChannelMode.DIGITAL, i + 1, (i % 2 == 1), "43")
            for i in range(30)
        ]

        update_mock.assert_called_once_with(expected)


@pytest.mark.asyncio
async def test_sender_update_test_analog():
    """Test when updated all states are send to the server. Test with analog states."""
    entities_ids = create_dummy_ids(ANALOG_DOMAINS[0], 30)
    sender = StateSenderV2(coe, entities_ids)

    with patch(COE_SEND_ANALOG_VALUES_V2_PACKAGE) as update_mock, patch(
        COE_SEND_DIGITAL_VALUES_V2_PACKAGE
    ):
        for i in range(30):
            sender.update_analog_manuel(entities_ids[str(i)], i % 10, "kW")

        await sender.update()

        expected = [
            CoEChannel(ChannelMode.ANALOG, i + 1, i % 10, "10") for i in range(30)
        ]

        actual = update_mock.call_args_list[0][0][0]

        update_mock.assert_called_once()

        assert len(actual) == len(expected)

        for expected_item, actual_item in zip(expected, actual):
            assert actual_item.mode == expected_item.mode
            assert actual_item.index == expected_item.index
            assert actual_item.value == expected_item.value
            assert actual_item.unit == expected_item.unit
