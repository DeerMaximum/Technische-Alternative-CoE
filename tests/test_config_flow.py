"""Test the Technische Alternative CoE config flow."""
from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from ta_cmi import ApiError

from custom_components.ta_coe.const import (
    CONF_CAN_IDS,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)
from tests import (
    COE_VERSION_CHECK_PACKAGE,
    COEAPI_RAW_REQUEST_PACKAGE,
)

DUMMY_HOST = "http://1.2.3.4"

DUMMY_CONNECTION_DATA: dict[str, Any] = {CONF_HOST: DUMMY_HOST, CONF_CAN_IDS: "19"}

DUMMY_DEVICE_API_DATA: dict[str, Any] = {
    "digital": [{"value": True, "unit": 43}],
    "analog": [{"value": 34.4, "unit": 1}],
    "last_update_unix": 1680410064.03764,
    "last_update": "2023-04-01T12:00:00",
}

DUMMY_CONFIG_ENTRY: dict[str, Any] = {
    CONF_HOST: "http://localhost",
}

DUMMY_ENTRY_CHANGE: dict[str, Any] = {
    CONF_SCAN_INTERVAL: 15,
}

DATA_OVERRIDE: dict[str, Any] = deepcopy(DUMMY_CONNECTION_DATA)

DUMMY_CONFIG_ENTRY_UPDATED: dict[str, Any] = {
    CONF_HOST: "http://localhost",
    CONF_SCAN_INTERVAL: 15,
}


@pytest.mark.asyncio
async def test_show_set_form(hass: HomeAssistant) -> None:
    """Test that the setup form is served."""

    with patch(
        COE_VERSION_CHECK_PACKAGE,
        side_effect=ApiError("Could not connect to server"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_step_user_connection_error(hass: HomeAssistant) -> None:
    """Test starting a flow by user but no connection found."""
    with patch(
        COE_VERSION_CHECK_PACKAGE,
        side_effect=ApiError("Could not connect to server"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data=deepcopy(DUMMY_CONNECTION_DATA),
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_step_user_unexpected_exception(hass: HomeAssistant) -> None:
    """Test starting a flow by user but with an unexpected exception."""
    with patch(
        COE_VERSION_CHECK_PACKAGE,
        side_effect=Exception("DUMMY"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data=deepcopy(DUMMY_CONNECTION_DATA),
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_step_user(hass: HomeAssistant) -> None:
    """Test starting a flow by user with valid values."""
    with patch(COE_VERSION_CHECK_PACKAGE, return_value=None):

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data=deepcopy(DUMMY_CONNECTION_DATA),
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "CoE"
        assert result["data"] == {
            CONF_HOST: DUMMY_HOST, CONF_CAN_IDS: [19]
        }


@pytest.mark.asyncio
async def test_user_addon_detection_only_first_instance(hass: HomeAssistant) -> None:
    """Test starting a flow by user but integration was already configured and addon check is disabled."""
    conf_entry: MockConfigEntry = MockConfigEntry(
        domain=DOMAIN, title="CoE", data={CONF_HOST: "http://192.168.2.101"}
    )

    conf_entry.add_to_hass(hass)

    with patch(COE_VERSION_CHECK_PACKAGE, return_value=None), patch(
        COEAPI_RAW_REQUEST_PACKAGE,
        return_value=DUMMY_DEVICE_API_DATA,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_step_user_with_addon_detected(hass: HomeAssistant) -> None:
    """Test starting a flow by user and addon is installed."""

    with patch(COE_VERSION_CHECK_PACKAGE, return_value=None) as api_mock, patch(
        COEAPI_RAW_REQUEST_PACKAGE,
        return_value=DUMMY_DEVICE_API_DATA,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        api_mock.assert_called_once()
