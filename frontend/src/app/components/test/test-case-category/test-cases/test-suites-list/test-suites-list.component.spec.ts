/* eslint-disable @typescript-eslint/naming-convention */
/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
import { TestBed } from '@angular/core/testing';
import { TestSandbox } from '../../../test.sandbox';
import { TestSuitesListComponent } from './test-suites-list.component';

class MockTestSandbox {
  getCurrentTestCategory() {
    return 0;
  }
  getRunTestCaseData() {
    return test_cases;
  }
  setDefaultSelectedData() { }
  setSelectedData() { }
  getSelectedData() {
    return Selected_test_cases;
  }
}

describe('TestSuitesListComponent', () => {
  let component: TestSuitesListComponent, testSandbox;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        TestSuitesListComponent,
        { provide: TestSandbox, useClass: MockTestSandbox }
      ]
    }).compileComponents();
    component = TestBed.inject(TestSuitesListComponent);
    testSandbox = TestBed.inject(TestSandbox);
  });
  it('check and uncheck mastercheckbox', () => {
    component.checkAndUncheckAll();
    expect(component.masterCheckBox).toBeTrue();
    component.checkAndUncheckAll();
    expect(component.masterCheckBox).toBeFalse();
  });
  it('checks selected children length', () => {
    Selected_test_cases = test_cases;
    expect(component.checkCurrentChildLength(0)).toBeFalse();
    Selected_test_cases = partically_selected;
    expect(component.checkCurrentChildLength(0)).toBeTrue();
  });
  it('checks all test-suites are selected', () => {
    Selected_test_cases = test_cases;
    expect(component.isPartiallySelected()).toBeFalse();
    Selected_test_cases = partically_selected;
    expect(component.isPartiallySelected()).toBeTrue();
  });

  it('checks is parent selected', () => {
    component.selectedCategories = test_cases;
    expect(component.isParentSelected(0)).toBeTrue();
    expect(component.isParentSelected(2)).toBeFalse();
  });
});

let Selected_test_cases: any;
// test case data
const test_cases = [
  [
    {
      'public_id': 'ChipToolPoCSuite',
      'version': '0.0.1',
      'title': 'This is a Proof of Concept of running chip-tool tests',
      'description': '',
      'key': 0,
      'children': [
        {
          'public_id': 'TC_BI_1_1',
          'version': '0.0.1',
          'title': '12.1.1. [TC-BI-1.1] Global attributes with server as DUT',
          'description': 'TC_BI_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_0'
        },
        {
          'public_id': 'TC_CC_3_4',
          'version': '0.0.1',
          'title': '3.2.15. [TC-CC-3.1 to 3.3 and 4.1 to 4.4] Color Hue and Saturation Controls',
          'description': 'TC_CC_3_4',
          'count': 1,
          'parentKey': 0,
          'key': '0_1'
        },
        {
          'public_id': 'TC_CC_5',
          'version': '0.0.1',
          'title': '3.2.15. [TC-CC-5.1 to 5.3] Color XY Controls',
          'description': 'TC_CC_5',
          'count': 1,
          'parentKey': 0,
          'key': '0_2'
        },
        {
          'public_id': 'TC_CC_6',
          'version': '0.0.1',
          'title': '3.2.15. [TC-CC-6.1 to 6.3] Color Temperature Controls',
          'description': 'TC_CC_6',
          'count': 1,
          'parentKey': 0,
          'key': '0_3'
        },
        {
          'public_id': 'TC_CC_7',
          'version': '0.0.1',
          'title': '3.2.15. [TC-CC-7.1 to 7.4] Enhanced Color Controls',
          'description': 'TC_CC_7',
          'count': 1,
          'parentKey': 0,
          'key': '0_4'
        },
        {
          'public_id': 'TC_CC_8',
          'version': '0.0.1',
          'title': '. [TC-CC-8] Color Loop Controls',
          'description': 'TC_CC_8',
          'count': 1,
          'parentKey': 0,
          'key': '0_5'
        },
        {
          'public_id': 'TC_DM_1_1',
          'version': '0.0.1',
          'title': '10.1.1. [TC-DM-1.1] Basic Cluster Server Attributes',
          'description': 'TC_DM_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_6'
        },
        {
          'public_id': 'TC_DM_3_1',
          'version': '0.0.1',
          'title': '10.3.1. [TC-DM-3.1] Network Commissioning Attributes',
          'description': 'TC_DM_3_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_7'
        },
        {
          'public_id': 'TC_FLW_1_1',
          'version': '0.0.1',
          'title': '27.1.1. [TC-FLW-1.1] Global attributes with server as DUT',
          'description': 'TC_FLW_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_8'
        },
        {
          'public_id': 'TC_OCC_1_1',
          'version': '0.0.1',
          'title': '24.1.1. [TC-OCC-1.1] Global attributes with server as DUT',
          'description': 'TC_OCC_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_9'
        },
        {
          'public_id': 'TC_OO_1_1',
          'version': '0.0.1',
          'title': '3.1.1. [TC-OO-1] Global attributes with server as DUT',
          'description': 'TC_OO_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_10'
        },
        {
          'public_id': 'TC_OO_2_1',
          'version': '0.0.1',
          'title': '3.2.1. [TC-OO-2] Attributes with server as DUT',
          'description': 'TC_OO_2_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_11'
        },
        {
          'public_id': 'TC_OO_2_2',
          'version': '0.0.1',
          'title': '3.2.2. [TC-OO-3] Primary functionality with server as DUT',
          'description': 'TC_OO_2_2',
          'count': 1,
          'parentKey': 0,
          'key': '0_12'
        },
        {
          'public_id': 'TC_TM_1_1',
          'version': '0.0.1',
          'title': '6.1.1. [TC-TM-1.1] Global attributes with server as DUT',
          'description': 'TC_TM_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_13'
        },
        {
          'public_id': 'TC_WNCV_1_1',
          'version': '0.0.1',
          'title': 'Window Covering [TC-WNCV-1.1] Global attributes with server as DUT',
          'description': 'TC_WNCV_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_14'
        },
        {
          'public_id': 'TC_WNCV_2_1',
          'version': '0.0.1',
          'title': 'Window Covering [TC-WNCV-2.1] Attributes with server as DUT',
          'description': 'TC_WNCV_2_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_15'
        }
      ]
    }
  ],
  []
];
// partically selected test cases
const partically_selected = [
  [
    {
      'public_id': 'ChipToolPoCSuite',
      'version': '0.0.1',
      'title': 'This is a Proof of Concept of running chip-tool tests',
      'description': '',
      'key': 0,
      'children': [
        {
          'public_id': 'TC_BI_1_1',
          'version': '0.0.1',
          'title': '12.1.1. [TC-BI-1.1] Global attributes with server as DUT',
          'description': 'TC_BI_1_1',
          'count': 1,
          'parentKey': 0,
          'key': '0_0'
        }
      ]
    }
  ],
  []
];
