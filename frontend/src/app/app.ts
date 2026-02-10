import {Component, computed, effect, inject, OnInit, signal, viewChild, ViewChild} from '@angular/core';
import {Dropdown, DropdownValue, DropdownValues} from './components/dropdown/dropdown';
import {EntityConfigList} from './components/entity-config-list/entity-config-list';
import {Hass} from './services/hass';
import {ConfigEntryMetadata, ExposedEntitiesConfig, ExposedEntityConfig} from './types';
import {Message} from './components/message/message';


@Component({
  selector: 'app-root',
  imports: [
    Dropdown,
    EntityConfigList,
    Message
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  private hass = inject(Hass);

  configEntries: DropdownValues = [];
  configEntryID = signal<string | null>(null);

  analogEntityIDs: string[] = [];
  digitalEntityIDs: string[] = [];

  entityConfig = signal<ExposedEntitiesConfig>({
    analog: [],
    digital: []
  });

  messageBox = viewChild.required(Message);

  async ngOnInit() {
    document.body.style.colorScheme = this.hass.isDarkMode() ? "dark" : "light";

    this.setupEntityIDS();
    await this.setupConfigEntryDropdown();
    await this.onConfigEntryChange(); //Initial change is not captured
  }

  async onConfigEntryChange() {
    const entryID = this.configEntryID()

    if (entryID == null)
      return;

    let config = await this.hass.getCurrentConfig(entryID);

    config.analog = this.addEmptySlots(config.analog);
    config.digital = this.addEmptySlots(config.digital);

    this.entityConfig.set(config);
  }

  async onSave() {
    const entryId = this.configEntryID();
    if (entryId === null)
      return;

    let reducedConfig = {
      analog: [...this.entityConfig().analog],
      digital: [...this.entityConfig().digital]
    };

    reducedConfig.digital = reducedConfig.digital.filter(value => value.entity_id.length > 0);
    reducedConfig.analog = reducedConfig.analog.filter(value => value.entity_id.length > 0);

    await this.hass.setCurrentConfig(entryId, reducedConfig);

    this.messageBox().showMessage("Config updated", 5000);
  }

  async setupConfigEntryDropdown() {
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

  setupEntityIDS() {
    const analogPlatforms = ["sensor", "input_number", "number"];
    const digitalPlatforms = ["binary_sensor", "input_boolean"];

    this.analogEntityIDs = this.hass.getEntityIDS(analogPlatforms);
    this.digitalEntityIDs = this.hass.getEntityIDS(digitalPlatforms);
  }

  addEmptySlots(slots: ExposedEntityConfig[]) {
    if (slots.length == 0)
      return [];

    const lastID = (slots.at(-1) as ExposedEntityConfig).id;
    const allIds = [...Array(lastID).keys()].map(value => value + 1);
    const existingIds = slots.map((entry) => entry.id);
    const missingIds = allIds.filter(id => !existingIds.includes(id));

    missingIds.forEach(id => {
      slots.push({
        id: id,
        entity_id: ""
      })
    });

    slots = slots.sort((a, b) => a.id - b.id);

    return slots;
  }
}
