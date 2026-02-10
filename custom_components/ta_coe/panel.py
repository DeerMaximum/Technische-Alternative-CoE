from pathlib import Path
import time

from homeassistant.components import panel_custom, frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from custom_components.ta_coe.const import DOMAIN, _LOGGER, PANEL_NAME, PANEL_TITLE, PANEL_ICON


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the panel"""
    www_path = Path(__file__).parent / "www"

    if hass.http is None:
        _LOGGER.error("hass.http is not available, cannot register panel")
        return

    # Register static path for the frontend assets
    await hass.http.async_register_static_paths([
        StaticPathConfig("/ta-coe-hass", str(www_path), False)
    ])

    wrapper_path = www_path / "panel-wrapper.js"
    if not wrapper_path.exists():
        _LOGGER.error("panel-wrapper.js not found in assets directory")
        return

    cache_bust = int(time.time())
    module_url = f"/ta-coe-hass/panel-wrapper.js?v={cache_bust}"

    try:
        hass.data.get("frontend_panels", {}).pop(DOMAIN, None)
        _LOGGER.info("Removed any existing panel registration")
    except:
        pass

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=DOMAIN,
        module_url=module_url,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
        config={},
        config_panel_domain=DOMAIN,
    )

    _LOGGER.info("ta_coe panel registered successfully with iframe wrapper")

def async_unregister_panel(hass: HomeAssistant) -> None:
    """Unregister the panel."""
    frontend.async_remove_panel(hass, DOMAIN)
    _LOGGER.info("ta_coe panel unregistered")