import {Component, computed, effect, inject, OnInit, signal} from '@angular/core';
import {Dropdown, DropdownValue, DropdownValues} from './components/dropdown/dropdown';
import {EntityConfigList} from './components/entity-config-list/entity-config-list';
import {Hass} from './services/hass';
import {ConfigEntryMetadata, ExposedEntitiesConfig} from './types';


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
  configEntryID = signal<string | null>(null);

  entityConfig = signal<ExposedEntitiesConfig>({
    analog: [],
    digital: []
  });

  async ngOnInit() {
    document.body.style.colorScheme = this.hass.isDarkMode() ? "dark" : "light";

    await this.setUpConfigEntryDropdown();
  }

  async onConfigEntryChange() {
    const entryID = this.configEntryID()

    if (entryID == null)
      return;

    const config = await this.hass.getCurrentConfig(entryID);
    this.entityConfig.set(config);
  }

  onSave() {
    if (this.configEntryID() === null)
      return;

    console.log(this.entityConfig());
  }

  protected async setUpConfigEntryDropdown() {
    const entries = await this.hass.getConfigEntries();

    this.configEntries = entries.map((entry: ConfigEntryMetadata) => {
      return {
        value: entry.entry_id,
        label: entry.title
      } as DropdownValue;
    });

    if (entries.length > 0) {
      this.configEntryID.set(entries[0].entry_id);
    }
  }
}
