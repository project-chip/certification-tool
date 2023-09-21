/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
/* eslint-disable @typescript-eslint/naming-convention */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TestSandbox } from '../../test.sandbox';
import { TestCasesComponent } from './test-cases.component';

let updatedFilteredData: any = [];

class MockTestSandbox {
  getTestSuiteCategory() {
    return [];
  }
  getRunTestCaseData() {
    return getRunTestCases();
  }
  setFilteredData(data: any) {
    updatedFilteredData = data;
  }
  setTestCaseQuery(data: any) { }
};

describe('TestCasesComponent', () => {
  let component: TestCasesComponent;
  let fixture: ComponentFixture<TestCasesComponent>;
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TestCasesComponent],
      providers: [
        { provide: TestSandbox, useClass: MockTestSandbox }
      ]
    }).compileComponents();
  });
  beforeEach(() => {
    fixture = TestBed.createComponent(TestCasesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('check onTestSearch', () => {
    expect(component.searchQuery).toBe('');
    component.searchQuery = 'tc_d';
    expect(component.searchQuery).toBe('tc_d');
    component.onTestSearch();
    expect(updatedFilteredData).toEqual(getUpdatedFilteredData());
  });
});


// Configuration: this function returns filtered testCaseData
function getRunTestCases() {
  return [
    [
      {
        'public_id': 'FirstChipToolSuite',
        'version': '0.0.1',
        'title': 'Test Suite run with chip-tool tests',
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
            'key': '0_0',
          },
          {
            'public_id': 'TC_DM_1_1',
            'version': '0.0.1',
            'title': '10.1.1. [TC-DM-1.1] Basic Cluster Server Attributes',
            'description': 'TC_DM_1_1',
            'count': 1,
            'parentKey': 0,
            'key': '0_6',
          },
          {
            'public_id': 'TC_DM_3_1',
            'version': '0.0.1',
            'title': '10.3.1. [TC-DM-3.1] Network Commissioning Attributes',
            'description': 'TC_DM_3_1',
            'count': 1,
            'parentKey': 0,
            'key': '0_7',
          }
        ]
      }
    ]
  ];
}

function getUpdatedFilteredData() {
  return [
    [
      {
        'public_id': 'FirstChipToolSuite',
        'version': '0.0.1',
        'title': 'Test Suite run with chip-tool tests',
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
            'key': '0_0',
            'filtered': false
          },
          {
            'public_id': 'TC_DM_1_1',
            'version': '0.0.1',
            'title': '10.1.1. [TC-DM-1.1] Basic Cluster Server Attributes',
            'description': 'TC_DM_1_1',
            'count': 1,
            'parentKey': 0,
            'key': '0_6',
            'filtered': true
          },
          {
            'public_id': 'TC_DM_3_1',
            'version': '0.0.1',
            'title': '10.3.1. [TC-DM-3.1] Network Commissioning Attributes',
            'description': 'TC_DM_3_1',
            'count': 1,
            'parentKey': 0,
            'key': '0_7',
            'filtered': true
          }
        ]
      }
    ]
  ];
}
