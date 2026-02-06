import {Component} from '@angular/core';
import {Dropdown} from './components/dropdown/dropdown';
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
  sample_config_entries = new Map<string, string>([
    ["entry_id_one", "First Entry"], ["entry_id_two", "Second Entry"]]
  );

}
