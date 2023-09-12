/* eslint-disable @typescript-eslint/naming-convention */
import { TestBed } from '@angular/core/testing';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { ProjectSandbox } from '../../project/project.sandbox';
import { TestSandbox } from '../../test/test.sandbox';
import { NavSandbox } from '../nav.sandbox';
import { TopNavComponent } from './top-nav.component';

class MockNavSandbox { }
class MockProjectsAPI { }
class MockProjectSandbox {
  getAllProjectData() {
    const projectData = [
      {
        'name': 'First Project',
        'dut_type': 'accessory',
        'id': 1
      },
      {
        'name': 'string',
        'dut_type': 'controller',
        'id': 7
      },
      {
        'name': 'Switch',
        'dut_type': 'accessory',
        'id': 9
      },
      {
        'name': 'printer',
        'dut_type': 'controller',
        'id': 11
      },
      {
        'name': 'testname29sep2',
        'dut_type': 'accessory',
        'id': 13
      }
    ];
    return projectData;
  }
}
class MockSharedAPI { }
class MockTestSandbox { }

describe('topNavComponent', () => {
  let component: TopNavComponent, navSandbox, projectSandbox, projectAPI, sharedAPI, testSandbox;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        TopNavComponent,
        { provide: NavSandbox, useClass: MockNavSandbox },
        { provide: ProjectsAPI, useClass: MockProjectsAPI },
        { provide: ProjectSandbox, useClass: MockProjectSandbox },
        { provide: SharedAPI, useClass: MockSharedAPI },
        { provide: TestSandbox, useClass: MockTestSandbox }
      ]
    }).compileComponents();
    component = TestBed.inject(TopNavComponent);
    navSandbox = TestBed.inject(NavSandbox);
    projectAPI = TestBed.inject(ProjectsAPI);
    projectSandbox = TestBed.inject(ProjectSandbox);
    sharedAPI = TestBed.inject(SharedAPI);
    testSandbox = TestBed.inject(TestSandbox);
  });
  // checks project length
  it('should return a value greater or equal to 0', () => {
    expect(component.getProjectDataLen()).toBeGreaterThanOrEqual(0);
  });

  it('should return a date in readable format', () => {
    const getTime = component.findTime(new Date);
    expect(getTime).toBe('Just Now');
  });
});
