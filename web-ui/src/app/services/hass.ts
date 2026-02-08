import {Injectable} from '@angular/core';
import {
  CustomHomeAssistant,
  ExposedEntitiesConfig, ExposedEntitiesConfigResponse, GetConfigEntryResponse, WindowWithHass
} from '../types';

@Injectable({
  providedIn: 'root',
})
export class Hass {
  hass: CustomHomeAssistant | undefined;

  constructor() {
    const parent = window.parent as WindowWithHass;
    this.hass = parent.hass;
    if (!parent.hass) {
      console.warn("No hass object found.");
    }
  }

  isDarkMode() {
    return this.hass?.themes?.darkMode ?? false;
  }

  async getConfigEntries() {
    const response = await this.hass?.callWS<GetConfigEntryResponse>({
      type: "ta_coe/config/list"
    });

    return response?.entries ?? [];
  }

  async getCurrentConfig(entryID: string) {
    const response = await this.hass?.callWS<ExposedEntitiesConfigResponse>({
      type: "ta_coe/expose/info",
      config_entry_id: entryID
    });

    const emptyConfig: ExposedEntitiesConfig = {
      analog: [],
      digital: []
    }

    return response?.config ?? emptyConfig;
  }

}
