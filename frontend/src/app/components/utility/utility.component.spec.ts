import { DatePipe } from '@angular/common';
import { TestBed } from '@angular/core/testing';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { MainAreaSandbox } from '../main-area/main-area.sandbox';
import { UtilityComponent } from './utility.component';

class MockUtilityProvider {
  // sets the uploaded JOSN file
  setTestReportData() {

  }
  returnData() {
    return [];
  }
}
describe('UtilityComponent', () => {
  let component: UtilityComponent;
  let mainAreaSandbox, sharedAPI, date;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        UtilityComponent,
        { provide: SharedAPI, useClass: MockUtilityProvider },
        { provide: MainAreaSandbox, useClass: MockUtilityProvider },
        { provide: DatePipe }
      ]
    })
      .compileComponents();
    component = TestBed.inject(UtilityComponent);
    mainAreaSandbox = TestBed.inject(MainAreaSandbox);
    sharedAPI = TestBed.inject(SharedAPI);
    date = TestBed.inject(DatePipe);
  });

  it('should return difference in time', () => {
    expect(component.getTimeDifference(0, 0)).toBe('-');
  });

  it('should return True or False', () => {
    expect(component.isFieldDisplayed(1)).toBe(true);
    expect(component.isFieldDisplayed(2)).toBe(false);
  });
});
