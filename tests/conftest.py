"""Fixtures for testing."""
from unittest import mock

import pytest

from tests import COE_VERSION_CHECK_PACKAGE


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable enable_custom_integrations"""
    yield


@pytest.fixture(scope="session", autouse=True)
def patch_coe_server_check(request):
    """Patch the ta-cmi CoE server version check."""
    patched = mock.patch(COE_VERSION_CHECK_PACKAGE)
    patched.__enter__()

    def unpatch():
        patched.__exit__(None, None, None)

    request.addfinalizer(unpatch)
