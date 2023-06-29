"""CoE state observer to update CAN values."""

from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event
from ta_cmi import CoE

from .const import _LOGGER, ANALOG_DOMAINS, DIGITAL_DOMAINS, TYPE_BINARY, TYPE_SENSOR


class StateObserver:
    """Handle state updates for configured entities."""

    def __init__(self, hass: HomeAssistant, coe: CoE, entity_list: list[str]):
        """Initialize."""
        self._hass = hass
        self._coe = coe
        self._entity_list = entity_list

        self._states = {TYPE_BINARY: {}, TYPE_SENSOR: {}}

        self._get_all_states()

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

    def _get_all_states(self) -> None:
        """Get all states from entities."""
        for entity_id in self._entity_list:
            state = self._hass.states.get(entity_id)
            domain = entity_id[0 : entity_id.find(".")]

            if state is None or not self._is_state_valid(state):
                continue

            if domain in ANALOG_DOMAINS:
                self._states[TYPE_SENSOR][entity_id] = float(state)

            if domain in DIGITAL_DOMAINS:
                self._states[TYPE_BINARY][entity_id] = bool(state)

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
            self._states[TYPE_SENSOR][new_state.entity_id] = float(new_state.state)

        if new_state.domain in DIGITAL_DOMAINS:
            self._states[TYPE_BINARY][new_state.entity_id] = bool(new_state.state)
