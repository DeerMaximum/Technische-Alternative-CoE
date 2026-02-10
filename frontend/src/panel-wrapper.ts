import type { HomeAssistant as CustomCardHomeAssistant } from 'custom-card-helpers';

interface HomeAssistant extends Omit<CustomCardHomeAssistant, 'services' | 'themes'> {
  themes: { darkMode: boolean };
}

declare const window: Window & {
  hass?: HomeAssistant;
};

class CoEPanelWrapper extends HTMLElement {
  private iframe: HTMLIFrameElement | null = null;
  private _hass: HomeAssistant | undefined = undefined;

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
    const bgColor = isDarkMode ? '#1C1C1C' : 'white';

    // Create iframe pointing to the app
    this.iframe = document.createElement('iframe');
    this.iframe.src = '/ta-coe-hass/index.html';
    this.iframe.style.width = '100%';
    this.iframe.style.height = '100%';
    this.iframe.style.border = 'none';
    this.iframe.style.display = 'block';
    this.iframe.style.background = bgColor;

    this.appendChild(this.iframe);
  }

  disconnectedCallback() {
    if (this.iframe) {
      this.removeChild(this.iframe);
      this.iframe = null;
    }
    // Clean up window properties
    window.hass = undefined;
  }
}

// Register the custom element
if (!customElements.get('ta_coe-panel')) {
  customElements.define('ta_coe-panel', CoEPanelWrapper);
}


