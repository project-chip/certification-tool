import { AfterViewInit, Component, OnInit } from '@angular/core';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { saveAs } from 'file-saver';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { APP_STATE } from 'src/app/shared/utils/constants';
import { SharedService } from 'src/app/shared/core_apis/shared-utils';

@Component({
  selector: 'app-test-log-toolbar',
  templateUrl: './test-log-toolbar.component.html',
  styleUrls: ['./test-log-toolbar.component.scss']
})
export class TestLogToolbarComponent {
  appState = APP_STATE;
  constructor(public testRunAPI: TestRunAPI, public sharedAPI: SharedAPI, public sharedService: SharedService) { }

  // Using Blob save the execution data as file
  saveExecHistoryAsFile() {
    const newTestRun: any = this.sharedAPI.getTestReportData();
    const newTestRunStr = JSON.stringify(newTestRun);
    const file = new Blob([newTestRunStr], { type: 'text/plain;charset=utf-8' });
    saveAs(file, newTestRun.title + '-' + newTestRun.id.toString() + '.json');
    this.sharedService.cursorBusy(false);
  }

  // Take latest execution data and download as file
  downloadExecHistory() {
    if (this.sharedAPI.getAppState() === APP_STATE[0]) {
      this.sharedService.cursorBusy(true);
      const newTestRun: any = this.testRunAPI.getRunningTestCasesRawData();
      this.testRunAPI.getTestReportData(newTestRun.id, this.saveExecHistoryAsFile.bind(this));
    }
  }

  // Download the logs as file
  downloadTestLogs() {
    if (this.sharedAPI.getAppState() === APP_STATE[0]) {
      this.sharedService.cursorBusy(true);
      this.testRunAPI.getLogs(this.testRunAPI.getRunningTestCasesRawData().id, this.saveLogs.bind(this), false);
    }
  }

  onLogsFilterKeyChange(event: any) {
    this.testRunAPI.setLogsFilterKey(event.target.value);
    this.testRunAPI.setHighlightedLog(0);
    const scrollElement: HTMLElement | null = document.querySelector('.log-console-parent .cdk-virtual-scroll-viewport');
    if (scrollElement) {
      scrollElement.scrollTop = 0;
    }
  }

  getFilteredLogsLegth() {
    if (this.testRunAPI.getLogsFilterKey()) {
      return this.testRunAPI.getTestLogs().filter((ele: any) =>
        ele.message.toLowerCase().includes(this.testRunAPI.getLogsFilterKey().toLowerCase())).length;
    } else {
      return this.testRunAPI.getTestLogs().length;
    }
  }

  onLogSearchUpAndDown(type: any) {
    const currentIndex = this.testRunAPI.getHighlightedLog();
    let newIndex = 0;
    const filteredLogsLegth = this.getFilteredLogsLegth();
    if (type === 'DOWN') {
      if (currentIndex === filteredLogsLegth - 1) {
        newIndex = 0;
      } else {
        newIndex = currentIndex + 1;
      }
    } else if (type === 'UP') {
      if (currentIndex === 0) {
        newIndex = filteredLogsLegth - 1;
      } else {
        newIndex = currentIndex - 1;
      }
    }
    this.testRunAPI.setHighlightedLog(newIndex);

    const className = '.logs_tr_index_' + newIndex;
    const highlightedElement: HTMLElement | null = document.querySelector(className);
    const scrollElement: HTMLElement | null = document.querySelector('.log-console-parent .cdk-virtual-scroll-viewport');
    if (highlightedElement) {
      highlightedElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (scrollElement) {
      const scrollTopVal = newIndex / filteredLogsLegth * scrollElement.scrollHeight;
      scrollElement.scrollTop = scrollTopVal;
    }
  }

  onKeydown(event: any) {
    if (event.key === 'Enter') {
      if (event.shiftKey) {
        this.onLogSearchUpAndDown('UP');
      } else {
        this.onLogSearchUpAndDown('DOWN');
      }
    }
  }
  saveLogs(data: any) {
    const file = new Blob([data], { type: 'text/plain;charset=utf-8' });
    saveAs(file, this.testRunAPI.getRunningTestCasesRawData().title + '.log');
    this.sharedService.cursorBusy(false);
  }
}
