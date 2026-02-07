import {Component, input} from '@angular/core';
import {EntityConfigEntry} from '../entity-config-entry/entity-config-entry';

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

  protected slot_count = 1;
  protected slot_limit = 60;

  sample_data: string[] = ['foo', 'bar'];

  onAdd() {
    if (this.slot_count >= this.slot_limit)
      return;
    this.slot_count++;
  }

  onSlotDelete() {
    this.slot_count--;
  }
}
