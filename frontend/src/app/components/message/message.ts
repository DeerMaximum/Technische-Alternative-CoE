import {Component} from '@angular/core';

@Component({
  selector: 'app-message',
  imports: [],
  templateUrl: './message.html',
  styleUrl: './message.scss',
})
export class Message {
  message: string = "";
  hidden: boolean = true;

  showMessage(message: string, timeoutMS: number) {
    this.message = message;
    this.hidden = false;

    setTimeout(() => {
      this.hidden = true;
    }, timeoutMS);
  }

}
