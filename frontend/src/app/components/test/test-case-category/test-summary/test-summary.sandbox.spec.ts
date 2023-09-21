/* eslint-disable no-use-before-define */
/* eslint-disable @typescript-eslint/no-use-before-define */
/* eslint-disable @typescript-eslint/naming-convention */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TestRunStore } from 'src/app/store/test-run-store';
import { TestSummarySandbox } from './test-summary.sandbox';


class MockTestRunStore {
  selectedTestCase: any = getSelectedTestCase();
  testSuiteCategory: any = { test_collections: { chip_tool_tests: {}, sample_tests: {} } };
};

describe('TestSummarySandbox', () => {
  let component: TestSummarySandbox;
  let fixture: ComponentFixture<TestSummarySandbox>;
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TestSummarySandbox,
        { provide: TestRunStore, useClass: MockTestRunStore }
      ]
    }).compileComponents();
    component = TestBed.inject(TestSummarySandbox);
    const dataService = TestBed.inject(TestRunStore);
  });

  it('check selectedDataSummary', () => {
    expect(component).toBeTruthy();
    expect(component.selectedDataSummary()).toEqual(formattedTestSummary());
  });

  it('check selectedDataSummary', () => {
    const expectedValue = ['chip_tool_tests', 'sample_tests'];
    expect(component.getTestSuiteCategory()).toEqual(expectedValue);
  });
});


// Configuration: It returns selectedTestCase JSON data
function getSelectedTestCase() {
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
          }
        ]
      }
    ],
    [
      {
        'public_id': 'CommissioningSampleTestSuite',
        'version': '1.2.3',
        'title': 'This is Commissioning Test Suite',
        'description': 'This is Commissioning Test Suite',
        'key': 0,
        'children': [
          {
            'public_id': 'TCCSSWifiDeviceCommissioning',
            'version': '1.2.3',
            'title': 'This is Test Case tccss_wifi_device_commissioning',
            'description': 'This Test Case is built to test the             wifi device commissioning',
            'count': 1,
            'parentKey': 0,
            'key': '0_0'
          }
        ]
      }
    ]
  ];
}

// Configuration: This is expected format for primeNG tree component used for test-summary
function formattedTestSummary() {
  return [
    {
      'label': 'chip_tool_tests',
      'children': [
        {
          'label': 'FirstChipToolSuite',
          'children': [
            {
              'label': 'TC_BI_1_1',
              'count': 1,
              'collapsedIcon': 'icon-folder-open',
              'expandedIcon': 'icon-folder-open'
            },
            {
              'label': 'TC_CC_3_4',
              'count': 1,
              'collapsedIcon': 'icon-folder-open',
              'expandedIcon': 'icon-folder-open'
            }
          ],
          'collapsedIcon': 'icon-folder-open',
          'expandedIcon': 'icon-folder-open',
          'expanded': true
        }
      ],
      'collapsedIcon': 'icon-folder-open',
      'expandedIcon': 'icon-folder-open',
      'expanded': true
    },
    {
      'label': 'sample_tests',
      'children': [
        {
          'label': 'CommissioningSampleTestSuite',
          'children': [
            {
              'label': 'TCCSSWifiDeviceCommissioning',
              'count': 1,
              'collapsedIcon': 'icon-folder-open',
              'expandedIcon': 'icon-folder-open'
            }
          ],
          'collapsedIcon': 'icon-folder-open',
          'expandedIcon': 'icon-folder-open',
          'expanded': true
        }
      ],
      'collapsedIcon': 'icon-folder-open',
      'expandedIcon': 'icon-folder-open',
      'expanded': true
    }
  ];
}
