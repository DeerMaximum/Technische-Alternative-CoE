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

  selectedValue = model<string | null>(null);

  onSelect(event: Select2UpdateEvent){
    const value = event.value as string | null;
    this.selectedValue.set(value);
  }
}
