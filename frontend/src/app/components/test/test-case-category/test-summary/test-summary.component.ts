import { Component, DoCheck, OnDestroy } from '@angular/core';
import { TreeNode } from 'primeng/api';
import { TestSummarySandbox } from './test-summary.sandbox';
@Component({
  selector: 'app-test-summary',
  templateUrl: './test-summary.component.html',
  styleUrls: ['./test-summary.component.scss']
})
export class TestSummaryComponent implements DoCheck {
  treeData: TreeNode[] = [];
  lastChanges = true;
  constructor(public testSummary: TestSummarySandbox) { }
  // it is a hook, get triggered when value changes
  ngDoCheck() {
    if (this.lastChanges !== this.testSummary.getOnClickChanges()) {
      this.treeData = this.testSummary.selectedDataSummary();
    }
    this.lastChanges = this.testSummary.getOnClickChanges();
  }
}
