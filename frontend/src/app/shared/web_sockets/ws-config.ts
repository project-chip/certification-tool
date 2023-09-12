import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '../../../environments/environment';
import { catchError, tap } from 'rxjs/operators';
import { EMPTY } from 'rxjs';
import { SharedAPI } from '../core_apis/shared';
import { SharedService } from '../core_apis/shared-utils';


export const dataServiceStateEnum = {
  'closed': 0,
  'ready': 1,
};

@Injectable({
  providedIn: 'root'
})
export class DataService {
  public socket$: WebSocketSubject<any> | any;  // TODO make this private and let components use messages$
  public messages$: any = null;
  public readyState = dataServiceStateEnum.closed;
  private webSocketURL = environment.webSocketBaseURL;
  constructor(private sharedService: SharedService, private sharedAPI: SharedAPI) { }
  close() {
    this.socket$.complete();
  }
  public connect(): void {

    if (!this.socket$ || this.readyState === dataServiceStateEnum.closed) {
      this.socket$ = this.getNewWebSocket();
      this.socket$.subscribe();
      this.messages$ = this.socket$.pipe(
        tap({
          error: error => {
            this.sharedService.showPopUp();
          },
        }), catchError(_ => EMPTY));
    }
  }
  public sendMessage(msg: any) {
    this.socket$.next(msg);
  }
  public send(data: any) {
    if (this.socket$) {
      this.socket$.next(data);
    } else {
      console.error('Did not send data, open a connection first');
    }
  }

  private getNewWebSocket() {
    return webSocket({
      url: this.webSocketURL,
      deserializer: (e: { data: any }) => e.data,
      openObserver: {
        next: () => {
          this.readyState = dataServiceStateEnum.ready;
        }
      },
      closeObserver: {
        next: () => {
          this.readyState = dataServiceStateEnum.closed;
        }
      }
    });
  }

}
