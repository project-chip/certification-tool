/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
/* eslint-disable @typescript-eslint/naming-convention */
import { TestBed } from '@angular/core/testing';
import { DomSanitizer } from '@angular/platform-browser';
import { DialogService } from 'primeng/dynamicdialog';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { SharedService } from 'src/app/shared/core_apis/shared-utils';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { TestSandbox } from '../test.sandbox';
import { TestExecutionHistoryComponent } from './test-execution-history.component';

class MockTestSandbox {
  getTestExecutionResult() {
    return testExecutionHistory;
  }
  getTestExecutionHistory(id: any) {
    return 0;
  }
  getArchivedTestResult() {
    return testExecutionHistory;
  }
}
class MockDomSanitizer {
  bypassSecurityTrustStyle() { }
}
class MockSharedAPI {
  getSelectedProjectType() {
    return { id: 1 };
  };
  setIsProjectTypeSelected() { }
}
class MockDialogService { }
class MockTestRunAPI { }
class MockSharedService { }
describe('TestExecutionHistoryComponent', () => {
  let component: TestExecutionHistoryComponent, testSandbox,
    domSanitizer, sharedAPI, dialogService, testRunAPI;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        TestExecutionHistoryComponent,
        { provide: TestSandbox, useClass: MockTestSandbox },
        { provide: DomSanitizer, useClass: MockDomSanitizer },
        { provide: SharedAPI, useClass: MockSharedAPI },
        { provide: DialogService, useClass: MockDialogService },
        { provide: TestRunAPI, useClass: MockTestRunAPI },
        { provide: SharedService, useClass: MockSharedService }
      ]
    }).compileComponents();
    component = TestBed.inject(TestExecutionHistoryComponent);
    testSandbox = TestBed.inject(TestSandbox);
    domSanitizer = TestBed.inject(DomSanitizer);
    sharedAPI = TestBed.inject(SharedAPI);
    dialogService = TestBed.inject(DialogService);
    testRunAPI = TestBed.inject(TestRunAPI);
  });
  it('should return a valid string', () => {
    expect(component.mystyle).toBeDefined();
  });
  it('it should match return', () => {
    expect(component.filterProjectId()).toEqual(testExecutionHistory.reverse());
  });
});

const testExecutionHistory = [
  {
    'title': 'UI_Test_Run_2021_9_21_17_20_7',
    'test_run_config_id': 1,
    'project_id': 1,
    'operator_id': null,
    'id': 1,
    'state': 'passed',
    'started_at': '2021-09-21T11:50:07.968195',
    'completed_at': '2021-09-21T11:50:27.461959',
    'test_case_stats': {
      'test_case_count': 11,
      'states': {
        'passed': 11
      }
    }
  },
  {
    'title': 'UI_Test_Run_2021_10_4_11_33_21',
    'test_run_config_id': 8,
    'project_id': 1,
    'operator_id': null,
    'id': 14,
    'state': 'error',
    'started_at': '2021-10-04T06:03:21.503544',
    'completed_at': '2021-10-04T06:03:31.884589',
    'test_case_stats': {
      'test_case_count': 9,
      'states': {
        'pending': 4,
        'executing': 1,
        'passed': 1,
        'error': 3
      }
    }
  }];
