import { Injectable } from '@angular/core';
import { TestRunStore } from 'src/app/store/test-run-store';
import { TestRunService } from '../test-run-utils';
import { EXECUTION_STATUS_COMPLETED } from '../utils/constants';
import { SharedAPI } from './shared';
import * as _ from 'lodash';
import { SharedService } from './shared-utils';

@Injectable()
export class TestRunAPI {
  public runningTestCases: any;
  unArchivedHistory: any = []; archivedHistory: any = [];
  unArchivedLimit = 0; archivedLimit = 0;
  setArchived = false; setUnarchived = false;
  constructor(private testRunService: TestRunService, private testRunStore: TestRunStore, private sharedAPI: SharedAPI,
    public sharedService: SharedService) {
    this.getOperatorData();
  }

  // Get running testcase filtered data
  getRunningTestCases() {
    this.runningTestCases = this.testRunStore.runningTestCases;
    return this.runningTestCases;
  }

  // Get running testcase raw data
  getRunningTestCasesRawData() {
    return this.testRunStore.runningTestCasesRawData;
  }

  // Set running testcase raw data
  setRunningTestCasesRawData(value: any) {
    return this.testRunStore.setRunningTestCasesRawData(value);
  }

  // Set running testcase filtered data
  setRunningTestCases(value: any) {
    this.testRunStore.setRunningTestCases(value);
  }

  // get's testsuite category
  getTestCollectionData() {
    return this.testRunStore.testSuiteCategory.test_collections;
  }

  // Get test-logs data
  getTestLogs() {
    return this.testRunStore.testLogs;
  }

  // Set test-logs data
  setTestLogs(value: any) {
    this.testRunStore.setTestLogs(value);
  }

  // Get test-logs data
  getSelectedOperator() {
    return this.testRunStore.selectedOperator;
  }

  // Set test-logs data
  setSelectedOperator(value: any) {
    this.testRunStore.setSelectedOperator(value);
  }

  // Get test-logs data
  getLogsFilterKey() {
    return this.testRunStore.logsFilterKey;
  }

  // Set test-logs data
  setLogsFilterKey(value: string) {
    this.testRunStore.setLogsFilterKey(value);
  }

  // Get highlighted-logs-id
  getHighlightedLog() {
    return this.testRunStore.highlightedLog;
  }

  // Set highlighted-logs-id
  setHighlightedLog(value: number) {
    this.testRunStore.setHighlightedLog(value);
  }

  // Get running testcase from backend and set to mobx-store
  getRunningTestsData() {
    return this.testRunService.getRunningTestsJson().subscribe(
      (data) => {
        this.testRunStore.setRunningTestCasesRawData(data);
        const filteredJson = this.filterTestRunJSON(_.cloneDeep(data));
        this.testRunStore.setRunningTestCases(filteredJson);
        this.getTestLogsJson();
        return data;
      }, err => {
        this.sharedService.showPopUp();
      });
  }

  getTestLogsJson() {
    this.testRunService.getTestLogs().subscribe(
      (data) => {
        this.testRunStore.setTestLogs(data);
      }, err => {
        this.sharedService.showPopUp();
      }
    );
  }

  // Filter running testacse data to Component required format
  /* eslint-disable max-len */
  filterTestRunJSON(testData: any) {
    return testData.test_suite_executions.map((ele: any, index: any) => {
      const testExec = ele.test_case_executions.map((eleExec: any, caseIndex: any) => {
        const stepExec = eleExec.test_step_executions.map((eleStep: any, stepIndex: any) => {
          const newObject3 = { 'key': 'test_step_execution_' + eleStep.id, 'testStepIndex': index + '' + '' + caseIndex + '' + stepIndex, 'name': eleStep.title, 'status': eleStep.state, 'children': [] };
          return newObject3;
        });
        const newObject2 = { 'key': 'test_case_execution_' + eleExec.id, 'name': eleExec.test_case_metadata.title, 'expanded': true, 'count': '1', 'status': eleExec.state, 'children': stepExec };
        return newObject2;
      });

      const newObject = {
        'key': 'test_suite_execution_' + ele.id, 'name': ele.test_suite_metadata.public_id, 'expanded': true, 'count': '1', 'status': ele.state,
        'progress': this.getProgressValue(testExec), 'children': testExec
      };
      return newObject;
    });
  }

  getProgressValue(testExec: any) {    // When Abort we need to set updated value
    const progress = Math.round(testExec.filter(
      (elem: any) => EXECUTION_STATUS_COMPLETED.includes(elem.status)).length / testExec.length * 100);
    return progress;
  }

  // Start execution and update initial value
  setRunningTestsDataOnStart(execId: any) {
    return this.testRunService.startTestRunExecution(execId).subscribe(
      (data) => {
        this.testRunStore.setRunningTestCasesRawData(data);   // Initial rawData added to get testExecution id.
        const filteredJson = this.filterTestRunJSON(_.cloneDeep(data));
        this.testRunStore.setRunningTestCases(filteredJson);
        return data;
      }, err => {
        if (err.status === 409) {
          this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Run Execution HTTP request Conflit' });
        } else {
          this.sharedService.showPopUp();
        }
      });
  }

  // Abort test execution and update execution status
  abortTestExecAndUpdateTestcase(execId: any) {
    return this.testRunService.abortTestExecution().subscribe(
      async (data) => {
        this.readRunningTestsRawData(execId, this.updateRunningTestcase.bind(this));
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution aborted' });
        return data;
      }, err => {
        if (err.status === 409) {
          this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error occured while aborting' });
        } else {
          this.sharedService.showPopUp();
        }
      });
  }

  // update execution status
  updateRunningTestcase(data: any) {
    const filteredJson = this.filterTestRunJSON(_.cloneDeep(data));
    this.testRunStore.setRunningTestCases(filteredJson);
  }

  async readRunningTestsRawDataAsync(execId: any, callback: any = null) {
    const testExecData = await this.testRunService.readTestRunExecutionAsync(execId);
    this.testRunStore.setRunningTestCasesRawData(testExecData);
    if (callback) {
      await callback(testExecData);
    }
    return testExecData;
  }

  // Read test-execution data using Id and store it in mobx-stores
  readRunningTestsRawData(execId: any, callback: any = null) {
    this.testRunService.getLogs(execId, true).subscribe(
      (data: any) => {
        data = data.replaceAll('}', '},');
        let modifiedData = '[' + data + '{"level": "", "timestamp": null, "message": "", "test_suite_execution_index": null, "test_case_execution_index": null}]';
        modifiedData = JSON.parse(modifiedData);
        this.testRunStore.setTestLogs(modifiedData);
      }, err => {
        this.sharedService.cursorBusy(false);
      }
    );
    return this.testRunService.readTestRunExecution(execId).subscribe(
      (data) => {
        this.testRunStore.setRunningTestCasesRawData(data);
        if (callback) {
          callback(data);
        }
        return data;
      }, err => {
        this.sharedService.showPopUp();
      });
  }
  getMockReport() {
    return this.testRunService.getRunningTestsJson().subscribe(data => {
      this.sharedAPI.setTestReportData(data);
      return data;
    });

  }
  getTestReportData(execId: any, callBack: any) {
    this.testRunService.readTestRunExecution(execId).subscribe(
      (data) => {
        this.sharedAPI.setTestReportData(data);
        if (callBack !== 0) {
          callBack();
          this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test Report downloaded sucessfully' });
        }
        return data;
      }, err => {
        this.sharedService.showPopUp();
      }
    );
  }

  // Create new test run config
  async createTestRunConfig(requestJson: any) {
    const testConfigData = await this.testRunService.createTestRunConfig(requestJson);
    return testConfigData;
  }

  // Create new test run execution
  createTestRunExecution(callback: any, testConfigId: number, selectedProjectId: number, testName: string, operatorId: any, description: any) {
    return this.testRunService.createTestRunExecution(testConfigId, selectedProjectId, testName, operatorId, description).subscribe(
      (data) => {
        callback(data.id);
        return data;
      }, err => {
        this.sharedService.showPopUp();
      });
  }

  // get test execution result and update in the store
  async getTestExecutionResult(isArchived: any, projectId: any) {
    this.sharedAPI.setTestExecutionLoader(false);
    (await this.testRunService.getTestExecutionResult(isArchived, projectId, this.getDatalimit(isArchived))).subscribe((data: any) => {
      if (isArchived) {
        if (data.length >= 250) {
          this.archivedHistory.push(...data);
          this.archivedLimit += 250;
          this.getTestExecutionResult(isArchived, projectId);
        } else {
          this.archivedHistory.push(...data);
          this.testRunStore.setArchivedTestResult(this.archivedHistory);
          this.setArchived = true;
          this.archivedHistory = [];
          this.archivedLimit = 0;
          this.checkTestData();
        }
      } else {
        if (data.length >= 250) {
          this.unArchivedHistory.push(...data);
          this.unArchivedLimit += 250;
          this.getTestExecutionResult(isArchived, projectId);
        } else {
          this.unArchivedHistory.push(...data);
          this.unArchivedLimit = 0;
          this.testRunStore.setTestExecutionResult(this.unArchivedHistory);
          this.setUnarchived = true;
          this.unArchivedHistory = [];
          this.checkTestData();
        }
      }
    }, err => {
      this.sharedAPI.setTestExecutionLoader(true);
      this.sharedService.showPopUp();
    });
  }
  checkTestData() {
    if (this.setArchived && this.setUnarchived) {
      this.setArchived = false; this.setUnarchived = false;
      this.sharedAPI.setTestExecutionLoader(true);
    }
  }
  getDatalimit(isArchived: any) {
    if (isArchived) {
      return this.archivedLimit;
    } else {
      return this.unArchivedLimit;
    }
  }

  // Get the test collection data and store it in mobx-store
  getDefaultTestCases(callBack: any) {
    this.sharedAPI.setTestCaseLoader(true);
    return this.testRunService.getDefaultTestCases().subscribe(
      (data) => {
        this.testRunStore.setTestSuiteCategory(data);
        this.testRunStore.setCurrentTestCategory(0);
        callBack();
      }, err => {
        this.sharedService.showPopUp();
      });
  }

  getOperatorData() {
    return this.testRunService.getOperatorData().subscribe(
      (data) => {
        this.testRunStore.setOperators(data);
      }, err => {
        this.sharedService.showPopUp();
      }
    );
  }

  setOperatorData(operator: any, callback: (data: any) => void) {
    return this.testRunService.setOperatorData(operator).subscribe(data => {
      this.getOperatorData();
      callback(data);
    }, err => {
      this.sharedService.showPopUp();
    });
  }
  deleteOperator(operator: any) {
    this.testRunService.deleteOperator(operator).subscribe(data => {
      this.getOperatorData();
    }, err => {
      this.sharedService.showPopUp();
    });
  }

  updateOperator(data: any) {
    this.testRunService.updateOperator(data).subscribe(status => {
      this.getOperatorData();
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Operator Name Updated' });
    }, err => {
      this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Failed to update operator ' });
    });
  }
  archiveTestRun(id: any) {
    this.testRunService.archiveTestRun(id).subscribe(data => {
      this.getTestExecutionResult(false, this.sharedAPI.getSelectedProjectType().id);
      this.getTestExecutionResult(true, this.sharedAPI.getSelectedProjectType().id);
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution archived' });
    }, err => {
      this.sharedService.showPopUp();
    });
  }

  unarchiveTestRun(id: any) {
    this.testRunService.unarchiveTestRun(id).subscribe(data => {
      this.getTestExecutionResult(false, this.sharedAPI.getSelectedProjectType().id);
      this.getTestExecutionResult(true, this.sharedAPI.getSelectedProjectType().id);
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution unarchived' });
    }, err => {
      this.sharedService.showPopUp();
    });
  }

  deleteTestRun(id: any) {
    this.testRunService.deleteTestRun(id).subscribe(data => {
      this.getTestExecutionResult(false, this.sharedAPI.getSelectedProjectType().id);
      this.getTestExecutionResult(true, this.sharedAPI.getSelectedProjectType().id);
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution deleted' });
    }, err => {
      this.sharedService.showPopUp();
    });
  }
  searchTestExecutionHistory(searchQuery: any, isArchived: any) {
    this.sharedAPI.setTestExecutionLoader(false);
    this.testRunService.searchTestExecutionHistory(searchQuery, isArchived, this.sharedAPI.getSelectedProjectType().id).subscribe((data) => {
      this.sharedAPI.setTestExecutionLoader(true);
      if (isArchived) {
        this.testRunStore.setArchivedTestResult(data);
      } else {
        this.testRunStore.setTestExecutionResult(data);
      }
    });
  }
  fileUpload(data: File, callBack: any) {
    this.testRunService.fileUpload(data).subscribe(res => {
      callBack('0');
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'File uploaded sucessfully' });
    }, err => {
      callBack('-1');
      this.sharedService.showPopUp();
    });
  }

  getLogs(logId: any, callBack: any, json: any) {
    this.testRunService.getLogs(logId, json).subscribe(data => {
      callBack(data);
      this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Logs downloaded sucessfully' });
    }, err => {
      this.sharedService.cursorBusy(false);
      this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in Logs download' });
    });
  }

  async getExecutionStatus() {
    return await this.testRunService.getExecutionStatus();
  }

  getApplicableTestCases(data: any, callBack: any) {
    this.testRunService.getApplicableTestCases(data).subscribe(e => {
      callBack(e);
    }, err => {
    });
  }
  importTestRun(data: any, projectId: number) {
    return this.testRunService.importTestRun(data, projectId);
  }
  exportTestRun(data: any, download: boolean) {
    return this.testRunService.exportTestRun(data, download);
  }
}

export function testExecutionTable() {
  const testExecutionTableData = [
    {
      tableName: 'Test',
      toolTip: 'Archive'
    },
    {
      tableName: 'Archived Test',
      toolTip: 'Unarchive'
    }
  ];
  return testExecutionTableData;
}
