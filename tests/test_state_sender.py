"""Test the Technische Alternative CoE state sender base."""

from ta_cmi import CoE

from custom_components.ta_coe.const import (
    CONF_ANALOG_ENTITIES,
    CONF_DIGITAL_ENTITIES,
    ConfEntityToSend,
)
from tests.common import StubStateSender

coe = CoE("")

DUMMY_SEND_CONFIG = {
    CONF_ANALOG_ENTITIES: [
        ConfEntityToSend(1, "sensor.1"),
        ConfEntityToSend(2, "sensor.3"),
    ],
    CONF_DIGITAL_ENTITIES: [
        ConfEntityToSend(1, "binary_sensor.2"),
        ConfEntityToSend(2, "binary_sensor.4"),
    ],
}


def test_sender_init_create_map_entity_id_to_index():
    """When sender is initialized then an entity id index mapping."""
    sender = StubStateSender(coe, DUMMY_SEND_CONFIG)

    assert sender._index_from_id == {
        "sensor.1": "0",
        "binary_sensor.2": "0",
        "sensor.3": "1",
        "binary_sensor.4": "1",
    }


def test_sender_has_entities_no_entities():
    """Test the has_entities function with no entities available."""
    sender = StubStateSender(coe, {CONF_ANALOG_ENTITIES: [], CONF_DIGITAL_ENTITIES: []})

    assert sender.has_entities() is False


def test_sender_has_entities_with_entities():
    """Test the has_entities function with entities available."""
    sender = StubStateSender(coe, DUMMY_SEND_CONFIG)

    assert sender.has_entities()
