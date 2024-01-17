"""CoE state observer to track state changes."""
from typing import Any

from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT, STATE_ON
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event
from ta_cmi import CoE

from .const import (
    _LOGGER,
    ANALOG_DOMAINS,
    DIGITAL_DOMAINS,
    FREE_SLOT_MARKER,
    TYPE_BINARY,
    TYPE_SENSOR,
)
from .state_sender import StateSender


class StateObserver:
    """Handle state updates for configured entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        coe: CoE,
        sender: StateSender,
        entity_list: dict[str, Any],
    ):
        """Initialize."""
        self._hass = hass
        self._coe = coe
        self._sender = sender
        self._entity_dict = entity_list
        self._entity_list = entity_list.values()

        self._states = {TYPE_BINARY: {}, TYPE_SENSOR: {}}

        async_track_state_change_event(
            self._hass, self._entity_list, self._update_listener
        )

    @staticmethod
    def _is_state_valid(state: str) -> bool:
        """Check if a state is valid."""
        return state not in ["unavailable", "unknown"]

    def _has_state_changed(self, state: State) -> bool:
        """Check if a state is new."""
        return (
            self._states[TYPE_BINARY].get(state.entity_id) != state.state
            and self._states[TYPE_SENSOR].get(state.entity_id) != state.state
        )

    async def get_all_states(self) -> None:
        """Get all states from entities."""
        _LOGGER.debug("Update all states")

        for entity_id in self._entity_list:
            if entity_id == FREE_SLOT_MARKER:
                continue

            state = self._hass.states.get(entity_id)
            domain = entity_id[0 : entity_id.find(".")]

            if state is None or not self._is_state_valid(state.state):
                continue

            if domain in ANALOG_DOMAINS:
                state_value = float(state.state)
                self._states[TYPE_SENSOR][entity_id] = state_value
                self._sender.update_analog_manuel(
                    entity_id,
                    state_value,
                    str(state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, "")),
                )

            if domain in DIGITAL_DOMAINS:
                state_value = state.state is STATE_ON
                self._states[TYPE_BINARY][entity_id] = state_value
                self._sender.update_digital_manuel(entity_id, state_value)

        await self._sender.update()

    @callback
    async def _update_listener(self, event: Event) -> None:
        """Handle state updates."""
        new_state: State | None = event.data.get("new_state", None)

        if (
            new_state is None
            or not self._is_state_valid(new_state.state)
            or not self._has_state_changed(new_state)
        ):
            return

        _LOGGER.debug(f"Handle new state {new_state.entity_id}: {new_state.state}")

        if new_state.domain in ANALOG_DOMAINS:
            state_value = float(new_state.state)

            self._states[TYPE_SENSOR][new_state.entity_id] = state_value

            await self._sender.update_analog(
                new_state.entity_id,
                state_value,
                str(new_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, "")),
            )

        if new_state.domain in DIGITAL_DOMAINS:
            state_value = new_state.state is STATE_ON
            self._states[TYPE_BINARY][new_state.entity_id] = state_value

            await self._sender.update_digital(new_state.entity_id, state_value)
