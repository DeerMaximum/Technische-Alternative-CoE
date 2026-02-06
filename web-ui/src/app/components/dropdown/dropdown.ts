import {Component, input, model} from '@angular/core';


@Component({
  selector: 'app-dropdown',
  imports: [

  ],
  templateUrl: './dropdown.html',
  styleUrl: './dropdown.scss',
})
export class Dropdown {
  heading = input.required<string>();
  values = input.required<Map<string, string>>();

  selected_value = model<string|null>(null);

  on_change(event: Event): void {
    event.stopPropagation();

    const target = event.target as HTMLSelectElement;

    this.selected_value.update(() => target.value);
  }
}
