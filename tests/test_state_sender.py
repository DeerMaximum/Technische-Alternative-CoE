"""Test the Technische Alternative CoE state sender base."""
from typing import Any

from ta_cmi import CoE

from custom_components.ta_coe.const import DIGITAL_DOMAINS
from custom_components.ta_coe.state_sender import StateSender
from tests import create_dummy_ids

coe = CoE("")


class StubStateSender(StateSender):
    def __init__(self, coe_intern: CoE, entity_list: dict[str, Any]):
        super().__init__(coe_intern, entity_list)

    async def update_digital(self, entity_id: str, state: bool) -> None:
        """Update a digital state with sending update."""
        pass

    async def update_analog(self, entity_id: str, state: float, unit: str) -> None:
        """Update an analog state with sending update."""
        pass

    async def update(self) -> None:
        """Send all values to the server."""
        pass


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
