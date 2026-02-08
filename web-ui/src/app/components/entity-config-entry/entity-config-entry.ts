import {Component, inject, input, model, output} from '@angular/core';
import {Select2, Select2Data, Select2UpdateEvent} from 'ng-select2-component';
import {ExposedEntityConfig} from '../../types';
import {Hass} from '../../services/hass';

const defaultPreviewValue: string = "---";

@Component({
  selector: 'app-entity-config-entry',
  imports: [
    Select2
  ],
  templateUrl: './entity-config-entry.html',
  styleUrl: './entity-config-entry.scss',
})
export class EntityConfigEntry {
  hass = inject(Hass);

  deletable = input(false);
  entity_ids = input.required({transform: transformToSelectData});
  entry = model.required<ExposedEntityConfig>();

  deleted = output<void>();

  previewValue = defaultPreviewValue;

  on_change(event: Select2UpdateEvent): void {
    const value = event.value as string | null ?? "";

    this.entry.update(oldValue => {
      oldValue.entity_id = value;
      return oldValue;
    })

    this.previewValue = this.hass.getEntityState(value) ?? defaultPreviewValue;
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
