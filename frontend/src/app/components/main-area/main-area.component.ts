import { Component } from '@angular/core';
import { ProjectSandbox } from '../project/project.sandbox';
import { MainAreaSandbox } from './main-area.sandbox';

@Component({
  selector: 'app-main-area',
  templateUrl: './main-area.component.html',
  styleUrls: ['./main-area.component.scss']
})

// This component will show the UI based on left-nav-bar tab selection.
export class MainAreaComponent {
  constructor(public mainAreaSandbox: MainAreaSandbox, public projectSandbox: ProjectSandbox) {
  }

  getIsNavBarVisible() {
    if (this.projectSandbox.getAllProjectData().length || this.projectSandbox.getArchivedProjects().length) {
      return 1;
    } else {
      return 0;
    }
  }
}
