import { Injectable } from '@angular/core';
import { Subscription } from 'rxjs';
import { TestExecutionSandbox } from 'src/app/components/test/test-execution/test-execution.sandbox';
import { APP_STATE, EXECUTION_STATUS_COMPLETED } from '../utils/constants';
import { DataService } from '../web_sockets/ws-config';
import { SharedAPI } from './shared';
import { TestRunAPI } from './test-run';
import * as _ from 'lodash';
import { SharedService } from './shared-utils';

@Injectable({ providedIn: 'root' })
export class WebSocketAPI {
  dataSubscription: Subscription | undefined;
  constructor(private testRunAPI: TestRunAPI, private dataService: DataService, public sharedAPI: SharedAPI,
    private sharedService: SharedService, public testExecutionSandbox: TestExecutionSandbox) { }

  async socketSubscription() {
    if (!this.dataSubscription) {
      // Use websocket to stream the logs
      this.dataSubscription = await this.dataService.messages$.subscribe(
        (data: any) => {
          const dataObject = JSON.parse(data);
          if (dataObject.type === 'test_update') {
            this.updateBufferData(dataObject);
            const runningTestcase = this.testRunAPI.getRunningTestCases();
            const updated = this.testExecutionSandbox.updateJSONBasedOnWebSocketData(runningTestcase, dataObject);
            this.testRunAPI.setRunningTestCases(updated);
          } else if (dataObject.type === 'prompt_request') {
            this.testExecutionSandbox.showExecutionPrompt(dataObject);
          } else if (dataObject.type === 'time_out_notification') {
            this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Failed to give input' });
            this.sharedAPI.setShowCustomPopup('');
          } else if (dataObject.type === 'test_log_records') {
            if (this.sharedAPI.getWebSocketLoader() === true) {
              this.sharedAPI.setWebSocketLoader(false);
            }
            const logs = _.cloneDeep(this.testRunAPI.getTestLogs());
            logs.push(...dataObject.payload);
            this.testRunAPI.setTestLogs(logs);
            this.checkExecutionEnded();
          } else if (dataObject.type === 'custom_upload') {
            this.testExecutionSandbox.showExecutionPrompt(dataObject);
          }
        });
    }
  }

  updateBufferData(dataObject: any) {
    if (this.sharedAPI.getExecutionStatus().state === '') {
      const updatedData = [...this.sharedAPI.getbufferWSData(), dataObject];
      this.sharedAPI.setbufferWSData(updatedData);
    } else if (this.sharedAPI.getbufferWSData().length && this.sharedAPI.getExecutionStatus().state === 'running') {
      this.sharedAPI.getbufferWSData().forEach((wsData: any) => {
        const runningTestcase = this.testRunAPI.getRunningTestCases();
        const updated = this.testExecutionSandbox.updateJSONBasedOnWebSocketData(runningTestcase, wsData);
        this.testRunAPI.setRunningTestCases(updated);
      });
      this.sharedAPI.setbufferWSData([]);
    }
  }

  checkExecutionEnded() {
    // TODO: BE having issue only with Sample tests to send the "Test Run" details in Websocket, So We are checking "Test Suite"
    const logs = _.cloneDeep(this.testRunAPI.getTestLogs());
    if (logs[logs.length - 1].message.includes('Test Run Completed')) {
      this.sharedAPI.setAppState(APP_STATE[0]);
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution completed' });
    }
  }

}
