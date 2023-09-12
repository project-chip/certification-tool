import { Injectable } from '@angular/core';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { TestRunStore } from 'src/app/store/test-run-store';
import * as  _ from 'lodash';
@Injectable()
export class TestSandbox {
  constructor(public testRunStore: TestRunStore, public testRunAPI: TestRunAPI, public sharedAPI: SharedAPI) {
  }
  // get's runtestcase data
  getRunTestCaseData() {
    return [...this.testRunStore.runTestCases];
  }
  // get's testsuite category
  getTestSuiteCategory() {
    const testSuite = Object.keys(this.testRunStore.testSuiteCategory.test_collections).map((data) => data);
    return testSuite;
  }
  // set's selected data in mobx
  setSelectedData(selectedData: any) {
    const defaulTestcases = _.cloneDeep(this.testRunStore.runTestCases);
    // eslint-disable-next-line prefer-const
    let selectedTestCases = _.cloneDeep(this.testRunStore.selectedTestCase);
    if (selectedData === -2) {
      selectedTestCases[this.getCurrentTestCategory()].length = 0;
    } else if (selectedData === -1) {
      selectedTestCases[this.getCurrentTestCategory()] = defaulTestcases[this.getCurrentTestCategory()];
    } else if (selectedTestCases[this.getCurrentTestCategory()][selectedData] === undefined ||
      selectedTestCases[this.getCurrentTestCategory()][selectedData] === null
      || selectedTestCases[this.getCurrentTestCategory()][selectedData].children.length !==
      defaulTestcases[this.getCurrentTestCategory()][selectedData].children.length) {
      selectedTestCases[this.getCurrentTestCategory()][selectedData] = defaulTestcases[this.getCurrentTestCategory()][selectedData];
    } else {
      selectedTestCases[this.getCurrentTestCategory()][selectedData] = undefined;
    }
    this.testRunStore.setSelectedTestCase(selectedTestCases);
  }
  // get's selected data
  getSelectedData() {
    return this.testRunStore.selectedTestCase;
  }
  // get's last checked
  getLastChecked() {
    return this.testRunStore.lastChecked;
  }
  // set's last checked
  setLastChecked(lastChecked: any) {
    this.testRunStore.setLastChecked(lastChecked);
  }
  // set's selected children in mobx
  setSelectedChild(data: any) {
    const selectedData = _.cloneDeep(this.testRunStore.selectedTestCase);
    if (data.length === 0) {
      selectedData[this.getCurrentTestCategory()][this.getLastChecked()] = undefined;
    } else {
      if (selectedData[this.getCurrentTestCategory()][data[0].parentKey]) {
        selectedData[this.getCurrentTestCategory()][data[0].parentKey].children = data;
      } else {
        selectedData[this.getCurrentTestCategory()][data[0].parentKey] =
          _.cloneDeep(this.getRunTestCaseData()[this.getCurrentTestCategory()][data[0].parentKey]);
        selectedData[this.getCurrentTestCategory()][data[0].parentKey].children = data;
      }
    }
    this.testRunStore.setSelectedTestCase(selectedData);
  }
  // set's onclick changes
  setOnClickChanges() {
    this.testRunStore.setOnClickChanges();
  }
  // get's onclick changes
  getOnClickChanges() {
    return this.testRunStore.onClickChange;
  }
  // set's current test screen (selection / execution)
  setTestScreen(value: any) {
    this.testRunStore.setTestScreen(value);
  }
  // get's current test screen (selection / execution)
  getTestScreen() {
    return this.testRunStore.testScreen;
  }
  // get's test execution result
  getTestExecutionResult() {
    return this.testRunStore.testExecutionResult;
  }
  // get's current test category
  getCurrentTestCategory() {
    return this.testRunStore.currentTestCategory;
  }
  // convert's object into array of objects in required format
  getTestData() {
    const testCollections = this.testRunStore.testSuiteCategory.test_collections;
    const testRunData: any = [];
    Object.keys(testCollections).forEach((testCategory, testCategoryIndex) => {
      const parsingData = testCollections[testCategory].test_suites;
      testRunData[testCategoryIndex] = [];
      Object.keys(parsingData).forEach((element, index) => {
        testRunData[testCategoryIndex][index] = parsingData[element].metadata;
        testRunData[testCategoryIndex][index].key = index;
        testRunData[testCategoryIndex][index].children = [];
        Object.keys(parsingData[element].test_cases).forEach((testCases, testCasesIndex) => {
          testRunData[testCategoryIndex][index].children[testCasesIndex] = parsingData[element].test_cases[testCases].metadata;
          testRunData[testCategoryIndex][index].children[testCasesIndex].count = 1;
          testRunData[testCategoryIndex][index].children[testCasesIndex].parentKey = index;
          testRunData[testCategoryIndex][index].children[testCasesIndex].key = index + '_' + testCasesIndex;
          testRunData[testCategoryIndex][index].children[testCasesIndex].picsKey = testCasesIndex;
        });
      });
    });
    this.testRunStore.setRunTestCases(testRunData);
    this.sharedAPI.setTestCaseLoader(false);
  }
  // set's current test category
  setCurrentTestCategory(category: any) {
    this.testRunStore.setCurrentTestCategory(category);
    this.testRunStore.setLastChecked(0);
  }
  // set's selected test cases
  setDefaultSelectedData(selectedData: any) {
    this.testRunStore.setSelectedTestCase(selectedData);
  }
  // Trigger core_apis function to create new test-run-config
  async createTestRunConfig(requestJson: any) {
    const testConfigData = await this.testRunAPI.createTestRunConfig(requestJson);
    return testConfigData;
  }
  // Trigger core_apis function to create new test-run-executions
  createTestRunExecution(callback: any, testConfigId: number, testName: string, operatorId: any, description: any) {
    const selectedProjectId = this.sharedAPI.getSelectedProjectType().id;
    this.testRunAPI.createTestRunExecution(callback, testConfigId, selectedProjectId, testName, operatorId, description);
  }
  // Start test execution and set initial running testcase data
  setRunningTestsDataOnStart(execId: any) {
    this.testRunAPI.setRunningTestsDataOnStart(execId);
  }
  // get operator data
  getOperatorData() {
    return this.testRunStore.operators;
  }
  // set operator data
  setOperatorData(operatorName: any, data: any) {
    return this.testRunAPI.setOperatorData(operatorName, data);
  }
  // delete operator data
  deleteOperator(operator: any) {
    this.testRunAPI.deleteOperator(operator);
  }
  //  update opeator
  updateOperator(data: any) {
    this.testRunAPI.updateOperator(data);
  }
  // get test case query
  getTestCaseQuery() {
    return this.testRunStore.testCaseQuery;
  }
  // set filtered data
  setFilteredData(filteredData: any) {
    this.testRunStore.setRunTestCases(filteredData);
  }
  // set test case query
  setTestCaseQuery(query: any) {
    this.testRunStore.setTestCaseQuery(query);
  }

  archiveTestRun(id: any) {
    this.testRunAPI.archiveTestRun(id);
  }

  unarchiveTestRun(id: any) {
    this.testRunAPI.unarchiveTestRun(id);
  }
  deleteTestRun(id: any) {
    this.testRunAPI.deleteTestRun(id);

  }
  getArchivedTestResult() {
    return this.testRunStore.archivedTestResult;
  }
  getTestExecutionResults(projectId: any) {
    this.testRunAPI.getTestExecutionResult(false, projectId);
    this.testRunAPI.getTestExecutionResult(true, projectId);
  }
  getDetectPicsChanges() {
    return this.testRunStore.detectPicsChanges;
  }
  setDetectPicsChanges(data: any) {
    this.testRunStore.setDetectPicsChanges(data);
  }
}
