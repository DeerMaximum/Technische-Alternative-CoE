import {Component, input, model} from '@angular/core';
import {Select2, Select2UpdateEvent} from 'ng-select2-component';


export interface DropdownValue {
  value: string;
  label: string;
}
export type DropdownValues = DropdownValue[]

@Component({
  selector: 'app-dropdown',
  imports: [
    Select2
  ],
  templateUrl: './dropdown.html',
  styleUrl: './dropdown.scss',
})
export class Dropdown {
  heading = input.required<string>();
  values = input.required<DropdownValues>();

  selected_value = model<string|null>(null);

  on_change(event:  Select2UpdateEvent): void {
    this.selected_value.update(() => event.value as string);
  }
}
