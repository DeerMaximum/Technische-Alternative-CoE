"""Test the Technische Alternative CoE state sender base."""

from ta_cmi import CoE

from custom_components.ta_coe.const import DIGITAL_DOMAINS
from tests import StubStateSender, create_dummy_ids

coe = CoE("")


def test_sender_init_create_map_entity_id_to_index():
    """When sender is initialized then an entity id index mapping."""
    entity_ids = {
        "0": "sensor.1",
        "1": "binary_sensor.2",
        "2": "sensor.3",
        "3": "binary_sensor.4",
    }

    sender = StubStateSender(coe, entity_ids)

    assert sender._index_from_id == {
        entity_ids["0"]: "0",
        entity_ids["1"]: "0",
        entity_ids["2"]: "1",
        entity_ids["3"]: "1",
    }


def test_sender_has_entities_no_entities():
    """Test the has_entities function with no entities available."""
    sender = StubStateSender(coe, {})

    assert sender.has_entities() is False


def test_sender_has_entities_with_entities():
    """Test the has_entities function with entities available."""
    sender = StubStateSender(coe, create_dummy_ids(DIGITAL_DOMAINS[0], 8))

    assert sender.has_entities()
