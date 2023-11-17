"""Tests for the Technische Alternative CoE integration."""
from typing import Any

COEAPI_PACKAGE = "ta_cmi.coe_api.CoEAPI.get_coe_data"
COE_SEND_ANALOG_VALUES_PACKAGE = "ta_cmi.coe.CoE.send_analog_values"
COE_SEND_DIGITAL_VALUES_PACKAGE = "ta_cmi.coe.CoE.send_digital_values"
COEAPI_RAW_REQUEST_PACKAGE = "ta_cmi.coe_api.CoEAPI._make_request_get"
COE_VERSION_CHECK_PACKAGE = "ta_cmi.coe.CoE._check_version"
SETUP_ENTRY_PACKAGE = "custom_components.ta_coe.async_setup_entry"
STATE_AVAILABLE_PACKAGE = "homeassistant.core.StateMachine.get"
STATE_SENDER_UPDATE_DIGITAL_MANUEL_PACKAGE = (
    "custom_components.ta_coe.state_sender.StateSender.update_digital_manuel"
)
STATE_SENDER_UPDATE_ANALOG_MANUEL_PACKAGE = (
    "custom_components.ta_coe.state_sender.StateSender.update_analog_manuel"
)
STATE_SENDER_UPDATE_DIGITAL_PACKAGE = (
    "custom_components.ta_coe.state_sender.StateSender.update_digital"
)
STATE_SENDER_UPDATE_ANALOG_PACKAGE = (
    "custom_components.ta_coe.state_sender.StateSender.update_analog"
)
STATE_SENDER_UPDATE = "custom_components.ta_coe.state_sender.StateSender.update"
OBSERVER_GET_ALL_STATES = (
    "custom_components.ta_coe.state_observer.StateObserver.get_all_states"
)
REFRESH_TASK_START_PACKAGE = "custom_components.ta_coe.refresh_task.RefreshTask.start"

DUMMY_DEVICE_API_DATA: dict[str, Any] = {
    "digital": [{"value": True, "unit": 43}],
    "analog": [
        {"value": 34.4, "unit": 1},
        {"value": 50, "unit": 11},
        {"value": 60, "unit": 12},
        {"value": 60, "unit": 19},
    ],
    "last_update_unix": 1680410064.03764,
    "last_update": "2023-04-01T12:00:00",
}
