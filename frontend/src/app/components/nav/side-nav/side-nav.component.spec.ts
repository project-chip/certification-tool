import { TestBed } from '@angular/core/testing';
import { ConfirmationService } from 'primeng/api';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { TestSandbox } from '../../test/test.sandbox';
import { NavSandbox } from '../nav.sandbox';
import { SideNavComponent } from './side-nav.component';

class MockSideNav {
  // get current component index
  getCurrentIndex() {
    return 1;
  }
}
describe('SideNavComponent', () => {
  let component: SideNavComponent, navSandbox, projectApi, confirmationService, testSandbox;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        SideNavComponent,
        { provide: NavSandbox, useClass: MockSideNav },
        { provide: ProjectsAPI, useClass: MockSideNav },
        { provide: ConfirmationService, useClass: MockSideNav },
        { provide: TestSandbox, useClass: MockSideNav }
      ]
    }).compileComponents();
    component = TestBed.inject(SideNavComponent);
    navSandbox = TestBed.inject(NavSandbox);
    projectApi = TestBed.inject(ProjectsAPI);
    confirmationService = TestBed.inject(ConfirmationService);
    testSandbox = TestBed.inject(TestSandbox);

  });

  it('should contain SideNavComponent', () => {
    expect(component).toBeTruthy();
    expect(component.sideBarClicked).toBeTruthy();
  });
});
