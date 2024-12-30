"""CoE state sender to send values V2."""
from typing import Any

from ta_cmi import ChannelMode, CoE, CoEChannel
from ta_cmi.const import UNITS_EN

from custom_components.ta_coe.const import _LOGGER
from custom_components.ta_coe.state_sender import StateSender


class StateSenderV2(StateSender):
    """Handle the transfer to the CoE server V2."""

    DIGITAL_UNIT = "43"

    def __init__(self, coe: CoE, entity_list: dict[str, Any]):
        """Initialize."""
        super().__init__(coe, entity_list)

    @staticmethod
    def _convert_unit_to_id(unit: str) -> str:
        """Convert the unit to an id."""
        unit_id: str = "0"
        for key, value in UNITS_EN.items():
            if unit == value:
                unit_id = key
                break

        if unit_id == "46":
            unit_id = "1"

        return unit_id

    async def update_digital(self, entity_id: str, state: bool):
        """Update a digital state with sending update."""
        self.update_digital_manuel(entity_id, state)

        _LOGGER.debug(f"Send digital update to server: {entity_id}")

        index = int(self._index_from_id[entity_id])
        coe_channel = CoEChannel(
            mode=ChannelMode.DIGITAL,
            index=index + 1,
            value=state,
            unit=self.DIGITAL_UNIT,
        )

        await self._coe.send_digital_values_v2([coe_channel])

    async def update_analog(self, entity_id: str, state: float, unit: str):
        """Update an analog state with sending update."""
        self.update_analog_manuel(entity_id, state, unit)

        _LOGGER.debug(f"Send digital update to server: {entity_id}")

        index = int(self._index_from_id[entity_id])
        coe_channel = CoEChannel(
            mode=ChannelMode.ANALOG,
            index=index + 1,
            value=state,
            unit=self._convert_unit_to_id(unit),
        )

        await self._coe.send_analog_values_v2([coe_channel])

    async def update(self):
        """Send all values to the server."""
        _LOGGER.debug(f"Send all {len(self._entity_list)} values to server")

        analog_channels = [
            CoEChannel(
                mode=ChannelMode.ANALOG,
                index=int(index) + 1,
                value=state.value,
                unit=self._convert_unit_to_id(state.unit),
            )
            for index, state in self._analog_states.items()
        ]

        digital_channels = [
            CoEChannel(
                mode=ChannelMode.DIGITAL,
                index=int(index) + 1,
                value=value,
                unit=self.DIGITAL_UNIT,
            )
            for index, value in self._digital_states.items()
        ]

        if len(analog_channels) != 0:
            await self._coe.send_analog_values_v2(analog_channels)

        if len(digital_channels) != 0:
            await self._coe.send_digital_values_v2(digital_channels)
