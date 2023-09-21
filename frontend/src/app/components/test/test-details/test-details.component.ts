/* eslint-disable indent */
/* eslint-disable @typescript-eslint/indent */
import { Component } from '@angular/core';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { APP_STATE } from 'src/app/shared/utils/constants';
import { TestSandbox } from '../test.sandbox';
import { environment } from 'src/environments/environment';
import { SharedService } from 'src/app/shared/core_apis/shared-utils';
import { TestRunStore } from 'src/app/store/test-run-store';
import * as _ from 'lodash';

@Component({
  selector: 'app-test-details',
  templateUrl: './test-details.component.html',
  styleUrls: ['./test-details.component.scss']
})
export class TestDetailsComponent {
  selectedDataFinal: any = {};
  testName = 'UI_Test_Run';
  description = '';
  allowedCharacter = /[^A-Za-z0-9 _-]/;
  constructor(public testSandbox: TestSandbox, public sharedAPI: SharedAPI,
    public testRunAPI: TestRunAPI, public sharedService: SharedService, public testRunStore: TestRunStore) {
    testRunAPI.getApplicableTestCases(this.sharedAPI.getSelectedProjectType().id, this.setDefaultPicsData.bind(this));
  }

  setDefaultPicsData(data: any) {
    const selectedData = _.cloneDeep(this.testRunStore.selectedTestCase);
    const defaultTestCase = _.cloneDeep(this.testSandbox.getRunTestCaseData());
    // eslint-disable-next-line prefer-const
    let detectPicsChanges: any = [];
    defaultTestCase.forEach((category: any, categoryIndex: any) => {
      detectPicsChanges[categoryIndex] = '';
      category.forEach((testSuite: any, testSuiteIndex: any) => {
        testSuite.children.forEach((testCase: any) => {
          data.test_cases.find((e: any) => {
            if (testCase.title === e) {
              if (selectedData[categoryIndex][testSuiteIndex]) {
                selectedData[categoryIndex][testSuiteIndex].children.push(testCase);
              } else {
                selectedData[categoryIndex][testSuiteIndex] = testSuite;
                selectedData[categoryIndex][testSuiteIndex].children = [];
                detectPicsChanges[categoryIndex] = true;
                selectedData[categoryIndex][testSuiteIndex].children.push(testCase);
              }
            }
          });
        });
      });
    });
    this.testRunStore.setSelectedTestCase(selectedData);
    this.testSandbox.setOnClickChanges();
    this.testRunStore.setDetectPicsChanges(detectPicsChanges);
  }
  // build's final data as object
  async onTestStart() {
    if (environment.isMockActive) {
      if (!this.testRunAPI.getSelectedOperator()) {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Select a operator' });
      } else {
        this.testSandbox.setTestScreen(1);
        this.testRunAPI.getRunningTestsData();
      }
    } else {
      if (!this.testRunAPI.getSelectedOperator()) {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Select a operator' });
      } else if (!this.isTestCaseSelected() && !this.isWarningExist()) {
        this.sharedAPI.setWebSocketLoader(true);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Test execution started' });
        this.sharedAPI.setAppState(APP_STATE[1]);
        this.testRunAPI.setRunningTestCasesRawData([]);
        this.testRunAPI.setRunningTestCases([]);
        this.testRunAPI.setTestLogs([]);
        this.testSandbox.setTestScreen(1);
        /* eslint-disable @typescript-eslint/naming-convention */
        this.selectedDataFinal = {
          'name': 'test',
          'dut_name': 'test_dut',
          'selected_tests': {}
        };
        /* eslint-enable @typescript-eslint/naming-convention */
        for (let mainIndex = 0; mainIndex < this.testSandbox.getSelectedData().length; mainIndex++) {
          if (this.testSandbox.getSelectedData()[mainIndex].length > 0) {
            this.selectedDataFinal.selected_tests[this.testSandbox.getTestSuiteCategory()[mainIndex]] = {};
            for (let parentIndex = 0; parentIndex < this.testSandbox.getSelectedData()[mainIndex].length; parentIndex++) {
              if (this.testSandbox.getSelectedData()[mainIndex][parentIndex]) {
                this.selectedDataFinal.selected_tests[this.testSandbox.getTestSuiteCategory()
                [mainIndex]][this.testSandbox.getSelectedData()[mainIndex][parentIndex].public_id] = {};
                this.testSandbox.getSelectedData()[mainIndex][parentIndex].children.forEach((selectedChildren: any) => {
                  this.selectedDataFinal.selected_tests[this.testSandbox.getTestSuiteCategory()[mainIndex]]
                  [this.testSandbox.getSelectedData()[mainIndex][parentIndex].public_id][selectedChildren.public_id] =
                    selectedChildren.count;
                });
              }
            }
          }
        }
        const testConfig: any = await this.testSandbox.createTestRunConfig(this.selectedDataFinal);
        this.testSandbox.createTestRunExecution(this.callbackForStartTestExecution.bind(this),
          testConfig.id, this.testName, this.testRunAPI.getSelectedOperator().id, this.description);
      }
    }
  }

  // call back for test execution
  callbackForStartTestExecution(value: any) {
    this.testSandbox.setRunningTestsDataOnStart(value);
  }

  isTestCaseSelected() {
    let selectedSuite = 0;
    this.testSandbox.getSelectedData().forEach((testCategory) => {
      if (testCategory) {
        testCategory.forEach((testSuite: any) => {
          if (testSuite) {
            if (testSuite.children.length > 0) {
              selectedSuite = 1;
            }
          }
        });
      }
    });
    if (selectedSuite === 1) {
      return false;
    } else {
      return true;
    }
  }

  isWarningExist() {     // If Test-run-config input has any warning it will return true
    let returnVal = false;
    if (this.testName === '' || this.allowedCharacter.test(this.testName)) {
      returnVal = true;
    }
    return returnVal;
  }
  clearTestSelection() {
    const emptySelection: any = [];
    for (let index = 0; index < this.testSandbox.getRunTestCaseData().length; index++) {
      emptySelection[index] = [];
    }
    this.testRunStore.setSelectedTestCase(emptySelection);
    this.testSandbox.setOnClickChanges();
  }
}
