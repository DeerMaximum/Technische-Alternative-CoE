import {Component, computed, input, model} from '@angular/core';
import {EntityConfigEntry} from '../entity-config-entry/entity-config-entry';
import {ExposedEntityConfig} from '../../types';

@Component({
  selector: 'app-entity-config-list',
  imports: [
    EntityConfigEntry
  ],
  templateUrl: './entity-config-list.html',
  styleUrl: './entity-config-list.scss',
})
export class EntityConfigList {
  heading = input.required<string>();
  entityIDS = input.required<string[]>();

  entries = model.required<ExposedEntityConfig[]>();

  slot_count = computed(() => this.entries().length);
  slot_limit = 60;

  onAdd() {
    if (this.slot_count() >= this.slot_limit)
      return;

    this.entries.update(oldValue => {
      const newValue: ExposedEntityConfig = {
        id: this.slot_count() + 1,
        entity_id: ""
      };

      return [...oldValue, newValue]
    })
  }

  onEntryChange(entry: ExposedEntityConfig) {
    this.entries.update(oldValue => {
      const index = entry.id - 1;
      return [...oldValue.slice(0, index), entry, ...oldValue.slice(index + 1)];
    });
  }

  onSlotDelete() {
    this.entries.update(oldValue => oldValue.slice(0, -1))
  }
}
