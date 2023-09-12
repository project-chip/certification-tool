import { Component } from '@angular/core';
import { ProjectSandbox } from './project.sandbox';

@Component({
  selector: 'app-project',
  templateUrl: './project.component.html',
  styleUrls: ['./project.component.scss']
})

// This component used to wrap project-details and device-details
export class ProjectComponent {
  isNewProjectClicked = false;
  constructor(public projectSandbox: ProjectSandbox) { }
}
