"""CoE state sender to send values."""
from dataclasses import dataclass
from typing import Any

from ta_cmi import CoE, CoEChannel
from ta_cmi.const import UNITS_EN, ChannelMode

from custom_components.ta_coe.const import _LOGGER, DIGITAL_DOMAINS


@dataclass
class AnalogValue:
    value: float
    unit: str


class StateSender:
    """Handle the transfer to the CoE server."""

    def __init__(self, coe: CoE, entity_list: dict[str, Any]):
        """Initialize."""
        self._coe = coe

        self._entity_list = entity_list
        self._index_from_id: dict[str, str] = {}
        self._digital_states: dict[str, bool] = {}
        self._analog_states: dict[str, AnalogValue] = {}

        self._init_digital_states()
        self._init_analog_states()
        self._init_generate_id_mapping()

    def has_entities(self) -> bool:
        """Check if the sender has entities in the entity_list"""
        return len(self._entity_list) > 0

    @staticmethod
    def _is_domain_digital(entity_id: str) -> bool:
        """Check if an entity domain is digital."""
        domain = entity_id[0 : entity_id.find(".")]
        return domain in DIGITAL_DOMAINS

    def _init_digital_states(self) -> None:
        """Create an empty digital states dict."""
        index = 0
        for entity_id in self._entity_list.values():
            if self._is_domain_digital(entity_id):
                self._digital_states[str(index)] = False
                index += 1

    def _init_analog_states(self) -> None:
        """Create an empty analog states dict."""
        index = 0
        for entity_id in self._entity_list.values():
            if not self._is_domain_digital(entity_id):
                self._analog_states[str(index)] = AnalogValue(0, "0")
                index += 1

    def _init_generate_id_mapping(self) -> None:
        """Create the entity index mapping."""
        digital_index = 0
        analog_index = 0
        for entity_id in self._entity_list.values():
            if self._is_domain_digital(entity_id):
                self._index_from_id[entity_id] = str(digital_index)
                digital_index += 1
            else:
                self._index_from_id[entity_id] = str(analog_index)
                analog_index += 1

    def update_digital_manuel(self, entity_id: str, state: bool):
        """Update a digital state without sending update."""
        _LOGGER.debug(f"Update digital value without update {entity_id}: {state}")
        index = self._index_from_id[entity_id]
        self._digital_states[index] = state

    def _build_digital_page(self):
        """Build the digital page."""
        page = [
            CoEChannel(ChannelMode.DIGITAL, i, state, "")
            for i, state in enumerate(self._digital_states.values(), 0)
        ]

        if len(page) < 32:
            page = page + [
                CoEChannel(ChannelMode.DIGITAL, i, False, "")
                for i in range(len(page), 32)
            ]

        return page

    async def update_digital(self, entity_id: str, state: bool):
        """Update a digital state with sending update."""
        self.update_digital_manuel(entity_id, state)
        index = int(self._index_from_id[entity_id])

        page = self._build_digital_page()

        _LOGGER.debug(f"Send digital update to server: {entity_id}")

        if index >= 15:
            await self._coe.send_digital_values(page[-16:], True)
        else:
            await self._coe.send_digital_values(page[:16], False)

    def update_analog_manuel(self, entity_id: str, state: float, unit: str):
        """Update analog state without sending update."""
        _LOGGER.debug(f"Update analog value without update {entity_id}: {state} {unit}")
        index = self._index_from_id[entity_id]
        self._analog_states[index] = AnalogValue(state, unit)

    @staticmethod
    def _convert_unit_to_id(unit: str) -> str:
        """Convert the unit to an id."""
        unit_id: str = "0"
        for key, value in UNITS_EN.items():
            if unit == value:
                unit_id = key
                break

        if unit_id == "1":
            unit_id = "46"

        return unit_id

    def _build_analog_page(self) -> list[CoEChannel]:
        """Build the analog page."""
        page = [
            CoEChannel(
                ChannelMode.ANALOG, i, state.value, self._convert_unit_to_id(state.unit)
            )
            for i, state in enumerate(self._analog_states.values(), 0)
        ]

        if len(page) < 32:
            page = page + [
                CoEChannel(ChannelMode.ANALOG, i, 0, "0") for i in range(len(page), 32)
            ]

        return page

    async def update_analog(self, entity_id: str, state: float, unit: str):
        """Update an analog state with sending update."""
        self.update_analog_manuel(entity_id, state, unit)
        index = int(self._index_from_id[entity_id])

        page = self._build_analog_page()

        _LOGGER.debug(f"Send analog update to server: {entity_id}")

        page_nr = index // 4
        index_first = page_nr * 4
        index_second = (page_nr + 1) * 4

        if page_nr == 0:
            index_first = 0

        await self._coe.send_analog_values(page[index_first:index_second], page_nr + 1)

    async def update(self):
        """Send all values to the server."""
        _LOGGER.debug(f"Send all {len(self._entity_list)} values to server")

        analog_page = self._build_analog_page()

        for page_nr in range(8):
            index_first = page_nr * 4
            index_second = (page_nr + 1) * 4

            if page_nr == 0:
                index_first = 0

            await self._coe.send_analog_values(
                analog_page[index_first:index_second], page_nr + 1
            )

        digital_page = self._build_digital_page()
        await self._coe.send_digital_values(digital_page[:16], False)
        await self._coe.send_digital_values(digital_page[-16:], True)
