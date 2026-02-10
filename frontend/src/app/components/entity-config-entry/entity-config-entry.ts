import {Component, inject, input, model, OnInit, output} from '@angular/core';
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
export class EntityConfigEntry implements OnInit {
  hass = inject(Hass);

  deletable = input(false);
  entity_ids = input.required({transform: transformToSelectData});
  entry = model.required<ExposedEntityConfig>();

  deleted = output<void>();

  selectedValue: string | null = null;

  previewValue = defaultPreviewValue;

  ngOnInit(): void {
    this.selectedValue = this.entry().entity_id;
    this.setPreviewValue(this.entry().entity_id);
  }

  on_change(event: Select2UpdateEvent): void {
    const value = event.value as string | null ?? "";

    this.entry.update(oldValue => {
      oldValue.entity_id = value;
      return oldValue;
    })

    this.setPreviewValue(value);
  }

  on_delete(): void {
    this.deleted.emit();
  }

  setPreviewValue(value: string): void {
    this.previewValue = this.hass.getEntityState(value) ?? defaultPreviewValue;
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
