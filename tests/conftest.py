"""Fixtures for testing."""

from copy import deepcopy
from typing import Generator
from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ta_coe import DOMAIN
from tests.const import COE_VERSION_CHECK_PACKAGE, DUMMY_CONFIG_ENTRY


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable enable_custom_integrations"""
    yield


@pytest.fixture(scope="session", autouse=True)
def patch_coe_server_check(request):
    """Patch the ta-cmi CoE server version check."""
    patched = mock.patch(COE_VERSION_CHECK_PACKAGE, return_value=None)
    patched.__enter__()

    def unpatch():
        patched.__exit__(None, None, None)

    request.addfinalizer(unpatch)


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.ta_coe.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Provide a common mock config entry."""
    config_entry: MockConfigEntry = MockConfigEntry(
        domain=DOMAIN,
        title="CoE",
        data=deepcopy(DUMMY_CONFIG_ENTRY),
        minor_version=2,
        version=1,
    )

    config_entry.add_to_hass(hass)

    return config_entry
