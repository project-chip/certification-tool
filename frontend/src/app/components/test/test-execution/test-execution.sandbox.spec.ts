/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
import { TestBed } from '@angular/core/testing';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { DataService } from 'src/app/shared/web_sockets/ws-config';
import { TestExecutionSandbox } from './test-execution.sandbox';


class MockDataService { };
class MockSharedAPI { };
class MockTestRunAPI { };
describe('TestExecutionSandbox', () => {
  let component: TestExecutionSandbox;
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TestExecutionSandbox,
        { provide: DataService, useClass: MockDataService },
        { provide: SharedAPI, useClass: MockSharedAPI },
        { provide: TestRunAPI, useClass: MockTestRunAPI }
      ]
    }).compileComponents();
    component = TestBed.inject(TestExecutionSandbox);
    const dataService = TestBed.inject(DataService);
    const sharedAPI = TestBed.inject(SharedAPI);
    const testRunAPI = TestBed.inject(TestRunAPI);
  });

  it('check updateJSONBasedOnWebSocketData', () => {
    expect(component).toBeTruthy();

    // Test 1: check Test suits update
    const updatedJson = component.updateJSONBasedOnWebSocketData(getTestData(), statusJson('testSuit'));
    const testSuitUpdate = JSON.parse(JSON.stringify(getTestData()));
    testSuitUpdate[0].status = 'executing';
    expect(updatedJson).toEqual(testSuitUpdate);

    // Test 2: check Test case update
    const testCaseUpdate = JSON.parse(JSON.stringify(testSuitUpdate));
    const updatedJson2 = component.updateJSONBasedOnWebSocketData(updatedJson, statusJson('testCase'));
    testCaseUpdate[0].progress = 100;
    testCaseUpdate[0].children[0].status = 'cancelled';
    expect(updatedJson2).toEqual(testCaseUpdate);

    // Test 3: check Test step update
    const testStepUpdate = JSON.parse(JSON.stringify(testCaseUpdate));
    const updatedJson3 = component.updateJSONBasedOnWebSocketData(updatedJson2, statusJson('testStep'));
    testStepUpdate[0].children[0].children[0].status = 'cancelled';
    expect(updatedJson3).toEqual(testStepUpdate);

  });
});

//  Configuration: It returns testData sample JSON.
function getTestData() {
  return [
    {
      'key': 'test_suite_execution_240',
      'name': 'FirstChipToolSuite',
      'expanded': true,
      'count': '1',
      'status': 'pending',
      'progress': 0,
      'children': [
        {
          'key': 'test_case_execution_951',
          'name': 'TC_BI_1_1',
          'expanded': true,
          'count': '1',
          'status': 'pending',
          'children': [
            {
              'key': 'test_step_execution_5543',
              'name': 'Starting ChipTool Test',
              'status': 'pending',
              'children': []
            },
            {
              'key': 'test_step_execution_5544',
              'name': 'read the global attribute: ClusterRevision',
              'status': 'pending',
              'children': []
            }
          ]
        }
      ]
    }
  ];
}

// Configuration: It returns sample status JSON.
function statusJson(param: any) {
  let returnJson = {};
  /* eslint-disable @typescript-eslint/naming-convention */
  if (param === 'testSuit') {
    returnJson = {
      'type': 'test_update',
      'payload': {
        'test_type': 'Test Suite',
        'body': {
          'test_suite_execution_id': 240,
          'state': 'executing',
          'errors': null
        }
      }
    };
  } else if (param === 'testCase') {
    returnJson = {
      'type': 'test_update',
      'payload': {
        'test_type': 'Test Case',
        'body': {
          'test_suite_execution_id': 240,
          'test_case_execution_id': 951,
          'state': 'cancelled',
          'errors': null
        }
      }
    };
  } else if (param === 'testStep') {
    returnJson = {
      'type': 'test_update',
      'payload': {
        'test_type': 'Test Step',
        'body': {
          'test_suite_execution_id': 240,
          'test_case_execution_id': 951,
          'test_step_execution_id': 5543,
          'state': 'cancelled',
          'errors': null,
          'failures': []
        }
      }
    };
  }
  /* eslint-enable @typescript-eslint/naming-convention */
  return returnJson;
}
