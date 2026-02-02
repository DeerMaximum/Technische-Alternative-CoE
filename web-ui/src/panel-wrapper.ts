/**
 * Minimal wrapper for Home Assistant panel integration.
 * This web component receives the hass object from HA, exposes it on window,
 * and loads the actual app in an iframe for proper document isolation.
 */
import type { HomeAssistant as CustomCardHomeAssistant } from 'custom-card-helpers';

interface HomeAssistant extends Omit<CustomCardHomeAssistant, 'services' | 'themes'> {
  themes: { darkMode: boolean };
}

// Type for window with hass
declare const window: Window & {
  hass?: HomeAssistant;
};

class CoEPanelWrapper extends HTMLElement {
  private _messageHandler?: (event: MessageEvent) => void;
  private iframe: HTMLIFrameElement | null = null;
  private _hass: HomeAssistant | undefined = undefined;

  // Properties that HA will set
  set hass(value: HomeAssistant | undefined) {
    this._hass = value;
    // Expose hass on window so iframe can access via window.parent.hass
    window.hass = value;
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    // Style the wrapper to fill the container
    this.style.display = 'block';
    this.style.width = '100%';
    this.style.height = '100%';
    this.style.position = 'relative';

    // Detect dark mode from hass to set initial background and avoid white flash
    const isDarkMode = this._hass?.themes?.darkMode ?? false;
    // These match the CSS variables in index.css:
    // Light: --background: 0 0% 100% (white)
    // Dark: --background: 222.2 84% 4.9% (dark blue)
    const bgColor = isDarkMode ? 'hsl(222.2, 84%, 4.9%)' : 'hsl(0, 0%, 100%)';

    // Create iframe pointing to the app
    this.iframe = document.createElement('iframe');
    this.iframe.src = '/ta-coe-hass/index.html';
    this.iframe.style.width = '100%';
    this.iframe.style.height = '100%';
    this.iframe.style.border = 'none';
    this.iframe.style.display = 'block';
    this.iframe.style.background = bgColor;

    this.appendChild(this.iframe);

    // Listen for messages from the iframe to trigger sidebar toggle
    this._messageHandler = (event: MessageEvent) => {
      // Only accept messages from our iframe
      if (event.source !== this.iframe?.contentWindow) return;
      if (event.data && event.data.type === 'COE_TOGGLE_SIDEBAR') {
        this.dispatchEvent(new Event('hass-toggle-menu', { bubbles: true, composed: true }));
      }
    };
    window.addEventListener('message', this._messageHandler);
  }

  disconnectedCallback() {
    if (this.iframe) {
      this.removeChild(this.iframe);
      this.iframe = null;
    }
    // Clean up window properties
    window.hass = undefined;
    if (this._messageHandler) {
      window.removeEventListener('message', this._messageHandler);
      this._messageHandler = undefined;
    }
  }
}

// Register the custom element
if (!customElements.get('ta_coe-panel')) {
  customElements.define('ta_coe-panel', CoEPanelWrapper);
}


