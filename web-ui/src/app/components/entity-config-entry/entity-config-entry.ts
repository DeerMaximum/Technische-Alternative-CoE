import {Component, input, output} from '@angular/core';
import {Select2, Select2Data, Select2UpdateEvent} from 'ng-select2-component';

@Component({
  selector: 'app-entity-config-entry',
  imports: [
    Select2
  ],
  templateUrl: './entity-config-entry.html',
  styleUrl: './entity-config-entry.scss',
})
export class EntityConfigEntry {

  index = input.required<number>();
  deletable = input(false);
  deleted = output<void>();

  entity_ids = input.required({transform: transformToSelectData});

  on_change(event:  Select2UpdateEvent): void {
      //TODO Fetch new state and update preview
  }

  on_delete(): void {
    this.deleted.emit();
  }
}

function transformToSelectData(values: string[]) {
  let result: Select2Data = [];

  values.forEach(value => {
    result.push({
      value: value, label: value
    });
  });

  return result;
}
