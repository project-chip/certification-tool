import { Component, Input } from '@angular/core';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { DEFAULT_POPUP_OBJECT } from 'src/app/shared/utils/constants';
import { DataService } from 'src/app/shared/web_sockets/ws-config';

@Component({
  selector: 'app-popup-modal',
  templateUrl: './popup-modal.component.html',
  styleUrls: ['./popup-modal.component.scss']
})
export class PopupModalComponent {
  @Input() popupId!: string;
  @Input() header!: string;
  @Input() subHeader!: string;
  @Input() buttons!: any;
  @Input() inputItems!: any;
  @Input() messageId!: any;
  fileName: any = '';
  file?: File;

  constructor(public sharedAPI: SharedAPI, private dataService: DataService) {
    this.fileName = '';

  }

  cancel(event: any) {
    const closeIcon = event.target.className;
    if (closeIcon.includes('p-dialog-header-close-icon')) {
      this.sharedAPI.setShowCustomPopup('');
      this.sharedAPI.setCustomPopupData(DEFAULT_POPUP_OBJECT);
      /* eslint-disable @typescript-eslint/naming-convention */
      const promptResponse = {
        'type': 'prompt_response', 'payload':
          { 'response': ' ', 'status_code': -1, 'message_id': this.messageId }
      };
      /* eslint-enable @typescript-eslint/naming-convention */
      this.dataService.send(promptResponse);
    }
  }
  onUpload(event: any) {
    this.file = event.target.files.item(0);
    this.fileName = this.file?.name;
  }
  checkInput(data: any) {
    if (this.fileName !== '' && this.popupId === 'FILE_UPLOAD_' + this.messageId) {
      return false;
    } else if (data && data[0].value || this.popupId === 'ABORT') {
      return false;
    } else {
      return true;
    }
  }
}
