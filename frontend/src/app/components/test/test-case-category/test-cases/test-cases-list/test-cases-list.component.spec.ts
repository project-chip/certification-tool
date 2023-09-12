/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
/* eslint-disable @typescript-eslint/naming-convention */
import { TestBed } from '@angular/core/testing';
import { TestSandbox } from '../../../test.sandbox';
import { TestCasesListComponent } from './test-cases-list.component';

class MockTestSandbox {
  getCurrentTestCategory() {
    return 0;
  }
  getLastChecked() {
    return 0;
  }
  setSelectedChild() {

  }
  getRunTestCaseData() {
    return test_cases;
  }
}
describe('TestCasesListComponent', () => {
  let component: TestCasesListComponent, testSandbox;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        TestCasesListComponent,
        { provide: TestSandbox, useClass: MockTestSandbox }
      ]
    }).compileComponents();
    component = TestBed.inject(TestCasesListComponent);
    testSandbox = TestBed.inject(TestSandbox);
  });
  it('should be a component', () => {
    expect(component).toBeTruthy();
  });
  it('check and unchecks master checkbox', () => {
    component.isMasterChecked();
    expect(component.masterCheckBox).toBeFalse();
    component.selectedCategories[0][0] = test_cases[0][0].children;
    component.isMasterChecked();
    expect(component.masterCheckBox).toBeTrue();
  });

  it('checks selected children', () => {
    expect(component.childrenSelected('0', '0_0')).toBeFalse();
    component.selectedCategories[0][0] = test_cases[0][0].children;
    expect(component.childrenSelected('0', '0_0')).toBeTrue();
  });

  it('checks partially selected', () => {
    expect(component.isPartiallySelected(0)).toBeFalse();
    component.selectedCategories[0][0] = [{ name: 'test' }];
    expect(component.isPartiallySelected(0)).toBeTrue();
  });
});


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
