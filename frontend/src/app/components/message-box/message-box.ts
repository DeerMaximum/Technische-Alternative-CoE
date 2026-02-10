import {Component} from '@angular/core';

@Component({
  selector: 'app-message-box',
  imports: [],
  templateUrl: './message-box.html',
  styleUrl: './message-box.scss',
})
export class MessageBox {
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
