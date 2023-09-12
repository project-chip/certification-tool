import { Component, OnDestroy } from '@angular/core';
import { TestSandbox } from '../../test.sandbox';

@Component({
  selector: 'app-test-cases',
  templateUrl: './test-cases.component.html',
  styleUrls: ['./test-cases.component.scss']
})
export class TestCasesComponent implements OnDestroy {
  searchQuery: any = '';
  constructor(public testSandbox: TestSandbox) {
    this.onTestSearch();
  }
  // to find the number of selectedtestcases
  getSelectedTestCase(index: number) {
    let count = 0;
    this.testSandbox.getSelectedData()[index].forEach((data: any, dataIndex: number) => {
      if (data && data.children.length === this.testSandbox.getRunTestCaseData()[index][dataIndex].children.length) {
        count++;
      }
    });
    return count;
  }
  // to set the current test category tab
  testCategoryClicked(category: any) {
    this.testSandbox.setCurrentTestCategory(category);
  }
  // search
  onTestSearch() {
    const filteredData = this.testSandbox.getRunTestCaseData();
    this.searchQuery = (this.searchQuery).toLowerCase();
    this.testSandbox.getRunTestCaseData().forEach((data: any, index: any) => {
      data.forEach((testSuite: any, testSuiteIndex: any) => {
        testSuite.children.forEach((testCase: any, testCaseIndex: any) => {
          const title = testCase.title.toLowerCase();
          filteredData[index][testSuiteIndex].children[testCaseIndex]['filtered'] = false;
          if (title.includes(this.searchQuery)) {
            filteredData[index][testSuiteIndex].children[testCaseIndex]['filtered'] = true;
          }
        });

      });
    });
    this.testSandbox.setTestCaseQuery(this.searchQuery);
    this.testSandbox.setFilteredData(filteredData);
  }

  scrollNavbar(data: any) {
    const ele = document.querySelector('.testcase-custom-view ul');

    if (ele && data === 'R') {
      ele.scrollLeft += 20;
    } else if (ele && data === 'L') {
      ele.scrollLeft -= 20;
    }
  }
  isNavbar(data: any) {
    const ele = document.querySelector('.testcase-custom-view ul');
    let isScroll = false;

    if (ele?.scrollLeft === 0 && data === 'RC') {
      ele.scrollLeft += 1;
      if (ele.scrollLeft > 0) {
        ele.scrollLeft = 0;
        isScroll = true;
      }
    } else if (ele && ele.scrollLeft > 0) {
      isScroll = true;
    }
    return isScroll;
  }
  ngOnDestroy() {
    this.testSandbox.setCurrentTestCategory(0);
  }
}
