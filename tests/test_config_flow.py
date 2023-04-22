"""Test the Technische Alternative CoE config flow."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from homeassistant import data_entry_flow
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from ta_cmi import ApiError

from custom_components.ta_coe.const import CONF_SCAN_INTERVAL, DOMAIN

from . import COEAPI_PACKAGE, COEAPI_RAW_REQUEST_PACKAGE

DUMMY_CONNECTION_DATA: dict[str, Any] = {CONF_HOST: "http://1.2.3.4"}

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

DUMMY_CONFIG_ENTRY_UPDATED: dict[str, Any] = {
    CONF_HOST: "http://localhost",
    CONF_SCAN_INTERVAL: 15,
}


@pytest.mark.asyncio
async def test_show_set_form(hass: HomeAssistant) -> None:
    """Test that the setup form is served."""

    with patch(
        COEAPI_PACKAGE,
        side_effect=ApiError("Could not connect to server"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"


@pytest.mark.asyncio
async def test_step_user_connection_error(hass: HomeAssistant) -> None:
    """Test starting a flow by user but no connection found."""
    with patch(
        COEAPI_PACKAGE,
        side_effect=ApiError("Could not connect to server"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=DUMMY_CONNECTION_DATA
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_step_user_unexpected_exception(hass: HomeAssistant) -> None:
    """Test starting a flow by user but with an unexpected exception."""
    with patch(
        COEAPI_PACKAGE,
        side_effect=Exception("DUMMY"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=DUMMY_CONNECTION_DATA
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_step_user(hass: HomeAssistant) -> None:
    """Test starting a flow by user with valid values."""
    with patch(
        COEAPI_PACKAGE,
        return_value=DUMMY_DEVICE_API_DATA,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}, data=DUMMY_CONNECTION_DATA
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == "CoE"


@pytest.mark.asyncio
async def test_step_user_with_addon_detected(hass: HomeAssistant) -> None:
    """Test starting a flow by user and addon is installed."""

    with patch(
        COEAPI_RAW_REQUEST_PACKAGE,
        return_value=DUMMY_DEVICE_API_DATA,
    ) as api_mock, patch(
        "custom_components.ta_coe.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == "CoE"
        assert result["data"] == {
            CONF_HOST: "http://a824d5a9_ta_coe:9000",
        }

        api_mock.assert_called_once_with("http://a824d5a9_ta_coe:9000/")


@pytest.mark.asyncio
async def test_options_flow_init(hass: HomeAssistant) -> None:
    """Test config flow options."""

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="CoE",
        data=DUMMY_CONFIG_ENTRY,
    )
    config_entry.add_to_hass(hass)

    with patch("custom_components.ta_coe.async_setup_entry", return_value=True):
        result = await hass.config_entries.options.async_init(config_entry.entry_id)

        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input=DUMMY_ENTRY_CHANGE,
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert dict(config_entry.options) == DUMMY_CONFIG_ENTRY_UPDATED
