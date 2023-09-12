import { AfterViewInit, ChangeDetectorRef, Component, Injectable } from '@angular/core';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { TestSandbox } from './test.sandbox';
import { SharedAPI } from 'src/app/shared/core_apis/shared';

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.scss']
})

@Injectable()
export class TestComponent implements AfterViewInit {
  constructor(public testRunAPI: TestRunAPI, public projectsAPI: ProjectsAPI, public testSandBox: TestSandbox,
    public sharedAPI: SharedAPI, public changeDetectorRef: ChangeDetectorRef) { }

  ngAfterViewInit() {
    this.changeDetectorRef.detectChanges();
  }
}
