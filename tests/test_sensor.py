"""Test the Technische Alternative CoE sensor."""

import pytest
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant.common import (
    MockConfigEntry,
    snapshot_platform,
)
from syrupy import SnapshotAssertion

from tests import setup_single_platform


@pytest.mark.asyncio
async def test_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the creation and values of the sensors."""

    await setup_single_platform(hass, mock_config_entry, Platform.SENSOR)
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)
