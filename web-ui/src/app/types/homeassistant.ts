import {HomeAssistant, Themes} from 'custom-card-helpers';


export interface WindowWithHass extends Window {
  hass?: CustomHomeAssistant;
}

export interface CustomHomeAssistant extends HomeAssistant {
  themes: CustomThemes;
}

export interface CustomThemes extends Themes{
  darkMode: boolean;
}

export interface GetConfigEntryResponse {
  entries: ConfigEntryMetadata[]
}

export interface ConfigEntryMetadata{
  title: string;
  entry_id: string;
}
