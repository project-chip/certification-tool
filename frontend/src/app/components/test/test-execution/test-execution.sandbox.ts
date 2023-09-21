import { Injectable } from '@angular/core';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { DEFAULT_POPUP_OBJECT, EXECUTION_STATUS_COMPLETED } from 'src/app/shared/utils/constants';
import { DataService } from 'src/app/shared/web_sockets/ws-config';

@Injectable()
export class TestExecutionSandbox {
  message: any = '';
  constructor(private dataService: DataService, public sharedAPI: SharedAPI, public testRunAPI: TestRunAPI) { }


  showExecutionPrompt(promptData: any) {
    // Converting the prompt BE json to component required JSON format.
    const buttons = [{ id: 1, label: 'Submit', class: 'buttonYes', callback: this.onYesClick.bind(this) }];
    const popupObject = {
      'popupId': '', 'subHeader': promptData.payload.prompt, 'header': ' ', 'buttons': buttons, 'inputItems': [] as any,
      'messageId': promptData.payload.message_id
    };

    if (promptData.payload.options) {             // Displaying the Radio button popup
      popupObject.popupId = 'RADIO_' + promptData.payload.message_id;
      const options = Object.entries(promptData.payload.options).map(([key, value]) => ({ key: value, value: key }));
      const inputItems = [
        {
          id: 1, type: 'radioButton', value: '', groupName: 'group_1',
          options: options
        }
      ];
      popupObject.inputItems = inputItems;
    } else if (promptData.payload.placeholder_text) {             // Displaying the Textbox popup
      popupObject.popupId = 'TEXTBOX_' + promptData.payload.message_id;
      const inputItems = [
        { id: 1, type: 'inputbox', value: promptData.payload.default_value, placeHolder: promptData.payload.placeholder_text }
      ];
      popupObject.inputItems = inputItems;
    } else if (promptData.payload.path) {             // Displaying the File-upload popup
      popupObject.popupId = 'FILE_UPLOAD_' + promptData.payload.message_id;
      const inputItems = [
        { id: 1, type: 'file_upload', value: '' }
      ];
      popupObject.inputItems = inputItems;
    }
    this.sharedAPI.setCustomPopupData(popupObject);
    this.sharedAPI.setShowCustomPopup(popupObject.popupId);
  }

  // This function will be called when user submit the popup.
  onYesClick(inputData: any, messageId: number, file: File) {
    this.sharedAPI.setShowCustomPopup('');
    this.sharedAPI.setCustomPopupData(DEFAULT_POPUP_OBJECT);
    if (inputData[0].type === 'file_upload') {
      this.message = messageId;
      this.testRunAPI.fileUpload(file, this.fileUploadCallback.bind(this));
    } else {
      /* eslint-disable @typescript-eslint/naming-convention */
      const promptResponse = {
        'type': 'prompt_response', 'payload':
          { 'response': inputData[0].value, 'status_code': 0, 'message_id': messageId }
      };
      /* eslint-enable @typescript-eslint/naming-convention */
      this.dataService.send(promptResponse);
    }
  }

  fileUploadCallback(status: any) {
    /* eslint-disable @typescript-eslint/naming-convention */
    const promptResponse = {
      'type': 'prompt_response', 'payload':
        { 'response': ' ', 'status_code': 0, 'message_id': this.message }
    };
    /* eslint-enable @typescript-eslint/naming-convention */
    this.dataService.send(promptResponse);
  }

  // Update Test execution status JSON using websocket data of particular testcase/suits data
  updateJSONBasedOnWebSocketData(testData: any, statusJson: any) {
    const suiteData = statusJson.payload.body;
    if (statusJson.payload.body.test_suite_execution_index > -1) {
      if (suiteData.test_step_execution_index > -1) {
        testData[suiteData.test_suite_execution_index].children[suiteData.test_case_execution_index].
          children[suiteData.test_step_execution_index].status = suiteData.state;
      } else if (suiteData.test_case_execution_index > -1) {
        testData[suiteData.test_suite_execution_index].children[suiteData.test_case_execution_index].status = suiteData.state;
      } else {
        testData[suiteData.test_suite_execution_index].status = statusJson.payload.body.state;
      }
      const updatedChild = testData[suiteData.test_suite_execution_index].children;
      testData[suiteData.test_suite_execution_index].progress = Math.round(updatedChild.filter(
        (elem: any) => EXECUTION_STATUS_COMPLETED.includes(elem.status)).length / updatedChild.length * 100);
    }
    return testData;
  }
}
