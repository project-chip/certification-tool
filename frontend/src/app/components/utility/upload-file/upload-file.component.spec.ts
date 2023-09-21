import { TestBed } from '@angular/core/testing';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { SharedService } from 'src/app/shared/core_apis/shared-utils';
import { UploadFileComponent } from './upload-file.component';

class MockUploadFile {
  returnData() {
    return [];
  }
}

describe('UploadFileComponent', () => {
  let component: UploadFileComponent;
  let sharedAPI, sharedService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      providers: [
        UploadFileComponent,
        { provide: SharedAPI, useClass: MockUploadFile },
        { provide: SharedService, useClass: MockUploadFile }
      ]
    })
      .compileComponents();
    component = TestBed.inject(UploadFileComponent);
    sharedAPI = TestBed.inject(SharedAPI);
    sharedService = TestBed.inject(SharedService);
  });

  it('should create UploadFileComponent', () => {
    expect(component).toBeTruthy();
    expect(component.onUpload).toBeTruthy();
  });
});
