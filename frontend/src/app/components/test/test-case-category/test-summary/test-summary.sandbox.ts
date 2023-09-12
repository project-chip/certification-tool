import { Injectable } from '@angular/core';
import { TestRunStore } from 'src/app/store/test-run-store';

@Injectable()
export class TestSummarySandbox {
  summaryData: any = [];
  constructor(public testRunStore: TestRunStore) { }
  // build's the required json format for p-tree
  selectedDataSummary() {
    let summaryIndex = 0, summaryParentIndex = 0;
    this.summaryData = [];
    const selectedData = this.testRunStore.selectedTestCase;
    for (let index = 0; index < selectedData.length; index++) {
      if (selectedData[index].length > 0 && selectedData[index] && this.checkChildren(selectedData[index])) {
        this.summaryData[summaryParentIndex] = {
          label: this.getTestSuiteCategory()[index], children: [],
          collapsedIcon: 'icon-folder-open', expandedIcon: 'icon-folder-open', expanded: true,
        };
        summaryIndex = 0;
        for (let selectedNameIndex = 0; selectedNameIndex < selectedData[index].length; selectedNameIndex++) {
          if (selectedData[index][selectedNameIndex]) {
            this.summaryData[summaryParentIndex]['children'][summaryIndex] = {
              label: selectedData[index][selectedNameIndex].title, children: [],
              collapsedIcon: 'icon-folder-open', expandedIcon: 'icon-folder-open', expanded: true,
            };
            selectedData[index][selectedNameIndex].children.forEach((child: any, childIndex: any) => {
              this.summaryData[summaryParentIndex]['children'][summaryIndex]['children'][childIndex] = {
                label: child.title, count: child.count, collapsedIcon: 'icon-folder-open', expandedIcon: 'icon-folder-open'
              };
            });
            summaryIndex++;
          }
        }
        summaryParentIndex++;
      }
    }
    return this.summaryData;
  }
  // checks children is valid
  checkChildren(selected: any) {
    let valid = false;
    for (let i = 0; selected.length > i; i++) {
      if (selected[i]) {
        valid = true;
      }
    }
    return valid;
  }
  // triggered when clicked on test-suit, test-case
  getOnClickChanges() {
    return this.testRunStore.onClickChange;
  }
  // gets the test_collection name
  getTestSuiteCategory() {
    const testSuite = Object.keys(this.testRunStore.testSuiteCategory.test_collections).map((data) => data);
    return testSuite;
  }
  getTestCaseLength() {
    return this.testRunStore.selectedTestCase.length;
  }
}


