import {Injectable} from '@angular/core';
import {
  CustomHomeAssistant,
  ExposedEntitiesConfig,
  ExposedEntitiesConfigResponse, GetConfigEntryResponse, WindowWithHass
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

  getLanguage(): string {
    return this.hass?.locale?.language ?? 'en';
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

  async setCurrentConfig(entryID: string, config: ExposedEntitiesConfig) {
    await this.hass?.callWS<void>({
      type: "ta_coe/expose/update",
      config_entry_id: entryID,
      config: config
    });
  }

  getEntityIDS(platforms: string[]) {
    const states = this.hass?.states;
    if (!states) return [];

    const allIDS = Object.keys(states);

    return allIDS.filter((id) => {
      const platform = id.split(".")[0];
      return platforms.indexOf(platform) !== -1;
    });
  }

  getEntityState(entityID: string) {
    const states = this.hass?.states;
    if (!states) return null;

    const state = states[entityID];
    if (!state) return null;

    const unit = state.attributes.unit_of_measurement ?? "";

    return `${state.state} ${unit}`
  }

}
