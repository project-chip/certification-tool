import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProjectSandbox } from '../project/project.sandbox';
import { MainAreaComponent } from './main-area.component';
import { MainAreaSandbox } from './main-area.sandbox';
class MockProjectSandbox {
  // This function is returning projectData
  getAllProjectData() {
    const data = [
      { name: 'harish' },
      { name: 'san' }, { name: 'ock' }];
    return data;
  }
  getArchivedProjects() {
    const data = [
      { name: 'harish' },
      { name: 'san' }, { name: 'ock' }];
    return data;
  }
};

describe('MainAreaComponent', () => {
  let component: MainAreaComponent;
  let fixture: ComponentFixture<MainAreaComponent>;
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MainAreaComponent],
      providers: [
        { provide: ProjectSandbox, useClass: MockProjectSandbox },
        { provide: MainAreaSandbox, useClass: MockProjectSandbox }
      ]
    }).compileComponents();
  });
  beforeEach(() => {
    fixture = TestBed.createComponent(MainAreaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should return a valid length', () => {
    expect(component.getIsNavBarVisible()).toBe(1);
  });
});
