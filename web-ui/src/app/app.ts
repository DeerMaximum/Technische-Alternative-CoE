import {Component, inject, OnInit} from '@angular/core';
import {Dropdown, DropdownValue, DropdownValues} from './components/dropdown/dropdown';
import {EntityConfigList} from './components/entity-config-list/entity-config-list';
import {Hass} from './services/hass';
import {ConfigEntryMetadata} from './types';


@Component({
  selector: 'app-root',
  imports: [
    Dropdown,
    EntityConfigList
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  private hass = inject(Hass);

  configEntries: DropdownValues = [];
  selectedEntry: string | null = null;

  async ngOnInit(){
    document.body.style.colorScheme = this.hass.isDarkMode() ? "dark" : "light";

    await this.setUpConfigEntryDropdown();
  }

  onSave(){
    if(this.selectedEntry === null)
      return;


  }

  protected async setUpConfigEntryDropdown(){
    const entries = await this.hass.getConfigEntries();

    this.configEntries = entries.map((entry: ConfigEntryMetadata) => {
      return {
        value: entry.entry_id,
        label: entry.title
      } as DropdownValue;
    });

    if(entries.length > 0){
      this.selectedEntry = entries[0].entry_id;
    }
  }
}
