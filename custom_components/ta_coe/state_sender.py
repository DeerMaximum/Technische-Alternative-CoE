"""CoE state sender base."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any

from ta_cmi import CoE

from custom_components.ta_coe.const import _LOGGER, DIGITAL_DOMAINS


@dataclass
class AnalogValue:
    value: float
    unit: str


class StateSender(metaclass=ABCMeta):
    """Base class to handle the transfer to the CoE server."""

    def __init__(self, coe: CoE, entity_list: dict[str, Any]):
        """Initialize."""
        self._coe = coe

        self._entity_list = entity_list
        self._index_from_id: dict[str, str] = {}

        self._digital_states: dict[str, bool] = {}
        self._analog_states: dict[str, AnalogValue] = {}

        self._init_generate_id_mapping()

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

    @staticmethod
    def _is_domain_digital(entity_id: str) -> bool:
        """Check if an entity domain is digital."""
        domain = entity_id[0 : entity_id.find(".")]
        return domain in DIGITAL_DOMAINS

    def has_entities(self) -> bool:
        """Check if the sender has entities in the entity_list"""
        return len(self._entity_list) > 0

    def update_digital_manuel(self, entity_id: str, state: bool):
        """Update a digital state without sending update."""
        _LOGGER.debug(f"Update digital value without update {entity_id}: {state}")
        index = self._index_from_id[entity_id]
        self._digital_states[index] = state

    @abstractmethod
    async def update_digital(self, entity_id: str, state: bool) -> None:
        """Update a digital state with sending update."""
        raise NotImplementedError("Method update_digital is not implemented")

    def update_analog_manuel(self, entity_id: str, state: float, unit: str):
        """Update analog state without sending update."""
        _LOGGER.debug(f"Update analog value without update {entity_id}: {state} {unit}")
        index = self._index_from_id[entity_id]
        self._analog_states[index] = AnalogValue(state, unit)

    @abstractmethod
    async def update_analog(self, entity_id: str, state: float, unit: str) -> None:
        """Update an analog state with sending update."""
        raise NotImplementedError("Method update_analog is not implemented")

    @abstractmethod
    async def update(self) -> None:
        """Send all values to the server."""
        raise NotImplementedError("Method update is not implemented")
