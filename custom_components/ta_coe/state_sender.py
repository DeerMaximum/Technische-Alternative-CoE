from abc import ABCMeta, abstractmethod
from typing import Any

from ta_cmi import CoE


class StateSender(metaclass=ABCMeta):
    """Base class to handle the transfer to the CoE server."""

    def __init__(self, coe: CoE, entity_list: dict[str, Any]):
        """Initialize."""
        self._coe = coe

        self._entity_list = entity_list

    @abstractmethod
    def update_digital_manuel(self, entity_id: str, state: bool) -> None:
        """Update a digital state without sending update."""
        raise NotImplementedError("Method update_digital_manuel is not implemented")

    @abstractmethod
    async def update_digital(self, entity_id: str, state: bool) -> None:
        """Update a digital state with sending update."""
        raise NotImplementedError("Method update_digital is not implemented")

    @abstractmethod
    def update_analog_manuel(self, entity_id: str, state: float, unit: str) -> None:
        """Update analog state without sending update."""
        raise NotImplementedError("Method update_analog_manuel is not implemented")

    @abstractmethod
    async def update_analog(self, entity_id: str, state: float, unit: str) -> None:
        """Update an analog state with sending update."""
        raise NotImplementedError("Method update_analog is not implemented")

    @abstractmethod
    async def update(self) -> None:
        """Send all values to the server."""
        raise NotImplementedError("Method update is not implemented")
