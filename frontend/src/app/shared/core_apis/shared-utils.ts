import { Injectable } from '@angular/core';
import { ConfirmationService, MessageService } from 'primeng/api';
import { SharedAPI } from './shared';
import * as Bowser from 'bowser';
@Injectable()
export class SharedService {
  constructor(public confirmationService: ConfirmationService, public messageService: MessageService, public sharedAPI: SharedAPI) { }
  cursorBusy(isTrue: boolean) {
    if (isTrue) {
      document.getElementsByTagName('body')[0].classList.add('cursor-busy');
    } else {
      document.getElementsByTagName('body')[0].classList.remove('cursor-busy');
    }
  }
  // pop-up if BE is failed to respond
  showPopUp() {
    this.confirmationService.confirm({
      message: 'Some thing went wrong',
      header: 'Failed to connect',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Retry',
      acceptIcon: 'pi pi-refresh',
      rejectVisible: false,
      closeOnEscape: false,
      accept: () => {
        window.location.reload();
      }
    });
  }
  // toast and notification
  setToastAndNotification(data: any) {
    this.messageService.add({ severity: data.status, summary: data.summary, detail: data.message });
    this.sharedAPI.setNotificationMessage({ state: data.status, message: data.message, time: new Date() });
  }
  findDate(date: any) {
    if (date) {
      const time = date.replace(/-/g, '/').replace(/\.(.*[0-9])/g, '').split('T');
      date = time[0] + ' ' + time[1] + ' UTC';
      const timeZone = new Date(date).toUTCString();
      if (timeZone.includes('PDT')) {
        date = time[0] + ' ' + time[1] + ' PDT';
      }
      const differenceInMinutes = Math.floor(((new Date().getTime() - new Date(date).getTime()) / (1000 * 60)));
      const differenceInHours = Math.floor(differenceInMinutes / 60);
      const differenceInDays = Math.floor(differenceInHours / 24);
      const differenceInMonths = Math.floor(differenceInDays / 30);
      const differenceInYears = Math.floor(differenceInDays / 365);

      if (differenceInMinutes <= 15) {
        return 'Just now';
      } else if (differenceInMinutes > 15 && differenceInMinutes <= 60) {
        return differenceInMinutes + ' minutes ago';
      } else if (differenceInHours >= 1 && differenceInHours <= 24) {
        return differenceInHours + ' hours ago';
      } else if (differenceInDays >= 1 && differenceInDays <= 30) {
        return differenceInDays + ' days ago';
      } else if (differenceInMonths >= 1 && differenceInMonths <= 12) {
        return differenceInMonths + ' months ago';
      } else if (differenceInYears >= 1 && differenceInYears < 5) {
        return differenceInYears + ' years ago';
      } else {
        return 'a while ago';
      }
    } else {
      return '-';
    }
  }
  checkBrowserAndVersion() {
    const browser = Bowser.getParser(window.navigator.userAgent);
    const isValid = browser.satisfies({
      chrome: '>=99.0.4844',
      edge: '>=96.0.1024.72',
      // eslint-disable-next-line @typescript-eslint/naming-convention
      Firefox: '>=97.0',
      safari: '>=12.1.2'

    });
    if (!isValid) {
      this.confirmationService.confirm({
        message: 'Your browser version is too old, please upgrade your browser to latest version to get all features of UI',
        header: 'Upgrade your browser to latest version',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Okay',
        rejectVisible: false,
        closeOnEscape: false,
        accept: () => {
        }
      });
    }
  }
}
