import {Component} from '@angular/core';
import {Dropdown, DropdownValues} from './components/dropdown/dropdown';
import {EntityConfigList} from './components/entity-config-list/entity-config-list';


@Component({
  selector: 'app-root',
  imports: [
    Dropdown,
    EntityConfigList
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  sample_config_entries: DropdownValues = [
    {value: "entry_id_one", label: "First Entry"},
    {value: "entry_id_two", label: "Second Entry"},
  ];

  onSave(){

  }
}
