"""CoE state sender base."""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from ta_cmi import CoE

from custom_components.ta_coe.const import (
    _LOGGER,
    DIGITAL_DOMAINS,
    CONF_ANALOG_ENTITIES,
    ConfEntityToSend,
    CONF_DIGITAL_ENTITIES,
)


@dataclass
class AnalogValue:
    value: float
    unit: str


class StateSender(metaclass=ABCMeta):
    """Base class to handle the transfer to the CoE server."""

    def __init__(self, coe: CoE, entity_config: dict[str, list[ConfEntityToSend]]):
        """Initialize."""
        self._coe = coe

        self._entity_config = entity_config
        self._index_from_id: dict[str, str] = {}

        self._digital_states: dict[str, bool] = {}
        self._analog_states: dict[str, AnalogValue] = {}

        self._init_generate_id_mapping()

    def _init_generate_id_mapping(self) -> None:
        """Create the entity index mapping."""

        for entity in self._entity_config.get(CONF_ANALOG_ENTITIES, []):
            self._index_from_id[entity.entity_id] = str(entity.id - 1)

        for entity in self._entity_config.get(CONF_DIGITAL_ENTITIES, []):
            self._index_from_id[entity.entity_id] = str(entity.id - 1)

    @staticmethod
    def _is_domain_digital(entity_id: str) -> bool:
        """Check if an entity domain is digital."""
        domain = entity_id[0 : entity_id.find(".")]
        return domain in DIGITAL_DOMAINS

    def has_entities(self) -> bool:
        """Check if the sender has entities in the entity_list"""
        return (
            len(self._entity_config[CONF_ANALOG_ENTITIES]) > 0
            or len(self._entity_config[CONF_DIGITAL_ENTITIES]) > 0
        )

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
