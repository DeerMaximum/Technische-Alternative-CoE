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
}
