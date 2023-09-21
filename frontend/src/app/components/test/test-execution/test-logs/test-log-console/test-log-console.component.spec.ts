/* eslint-disable @typescript-eslint/naming-convention */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { APP_STATE } from 'src/app/shared/utils/constants';
import { TestLogConsoleComponent } from './test-log-console.component';


class MockTestRunAPI {
  getTestLogs() {
    return [];
  }
  getLogsFilterKey() {
    return [];
  }
};
class MockSharedAPI {
  getAppState() {
    return APP_STATE[0];
  }
};

describe('TestLogConsoleComponent', () => {
  let component: TestLogConsoleComponent;
  let fixture: ComponentFixture<TestLogConsoleComponent>;
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TestLogConsoleComponent],
      providers: [
        { provide: TestRunAPI, useClass: MockTestRunAPI },
        { provide: SharedAPI, useClass: MockSharedAPI }
      ]
    }).compileComponents();
  });
  beforeEach(() => {
    fixture = TestBed.createComponent(TestLogConsoleComponent);
    component = fixture.componentInstance;
    spyOn(component, 'scrollToBottom');
    fixture.detectChanges();
  });

  // Configuration: Below json are sample logs data.
  const infoLog = {
    'level': 'INFO',
    'timestamp': 1640877078.176987,
    'message': 'Test Run Executing',
    'test_suite_execution_id': null,
    'test_case_execution_id': null
  };

  const testSuitsAndErrorLog = {
    'level': 'ERROR',
    'timestamp': 1640877078.224148,
    'message': 'Test Suite Executing: This is Test Suite 1',
    'test_suite_execution_id': 243,
    'test_case_execution_id': null
  };

  const testCaseAndWarningLog = {
    'level': 'WARNING',
    'timestamp': 1640877078.255148,
    'message': 'Executing Test Case: This is Test Case tcss1001',
    'test_suite_execution_id': 243,
    'test_case_execution_id': 954
  };
  it('check getLogCategory', () => {
    expect(component).toBeTruthy();
    // Test: check function is returning the valid classname based on the passed data.
    expect(component.getLogCategory(infoLog)).toEqual('info-log');
    expect(component.getLogCategory(testSuitsAndErrorLog)).toEqual('error-log testsuits-log');
    expect(component.getLogCategory(testCaseAndWarningLog)).toEqual('warning-log testcase-log');
  });

  it('check getPrefixChar', () => {
    expect(component).toBeTruthy();
    // Test: check function is returning valid prefix character based on log data
    expect(component.getPrefixChar(infoLog)).toEqual('');
    expect(component.getPrefixChar(testSuitsAndErrorLog)).toEqual(' * ');
    expect(component.getPrefixChar(testCaseAndWarningLog)).toEqual(' - ');
  });

  it('check logs auto scroll', () => {
    expect(component).toBeTruthy();
    // Test: check "autoScrollToBottom" value when we update values from other functions.
    expect(component.autoScrollToBottom).toBeTruthy();
    component.onUserScroll();
    expect(component.autoScrollToBottom).toBeFalsy();
    component.onAutoScrollIconClick();
    expect(component.autoScrollToBottom).toBeTruthy();
    expect(component.scrollToBottom).toHaveBeenCalledTimes(3);
  });
});
