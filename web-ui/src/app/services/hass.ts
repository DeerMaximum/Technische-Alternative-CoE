import {Injectable} from '@angular/core';
import {CustomHomeAssistant, WindowWithHass} from '../types';

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

  isDarkMode(){
    return this.hass?.themes?.darkMode ?? false;
  }
}
