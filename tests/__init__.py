"""Tests for the Technische Alternative CoE integration."""

from ta_cmi import CoE

from custom_components.ta_coe import ConfEntityToSend
from custom_components.ta_coe.state_sender import StateSender


def create_dummy_conf_entity_to_send(domain: str, count: int) -> list[ConfEntityToSend]:
    """Create dummy entity id dict."""
    dummy_data = []

    for i in range(1, count + 1):
        dummy_data.append(ConfEntityToSend(i, f"{domain}.{i}"))

    return dummy_data


class StubStateSender(StateSender):
    def __init__(
        self, coe_intern: CoE, entity_config: dict[str, list[ConfEntityToSend]]
    ):
        super().__init__(coe_intern, entity_config)

    async def update_digital(self, entity_id: str, state: bool) -> None:
        """Update a digital state with sending update."""
        pass

    async def update_analog(self, entity_id: str, state: float, unit: str) -> None:
        """Update an analog state with sending update."""
        pass

    async def update(self) -> None:
        """Send all values to the server."""
        pass
