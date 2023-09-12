import { Component } from '@angular/core';
import { MessageService } from 'primeng/api';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { SharedService } from 'src/app/shared/core_apis/shared-utils';

@Component({
  selector: 'app-upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.scss']
})
export class UploadFileComponent {
  data: any = '';
  fileName = '';
  fileSize = '';
  constructor(public sharedAPI: SharedAPI, public sharedService: SharedService) { }

  onUpload(event: any) {
    const file: File = event.target.files.item(0);
    if (file.type === 'application/json') {
      this.fileName = file.name;
      const fileReader = new FileReader();
      fileReader.onload = (e) => {
        this.data = fileReader.result;
        this.sharedAPI.setTestReportData(JSON.parse(this.data));
      };
      fileReader.readAsText(file);
    } else {
      this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Upload a valid JSON file' });
    }
  }
}
