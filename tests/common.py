from ta_cmi import CoE

from custom_components.ta_coe import ConfEntityToSend, StateSender


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
