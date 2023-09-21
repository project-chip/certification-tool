import { Component, Injectable } from '@angular/core';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { NavSandbox } from '../../nav/nav.sandbox';
import { ProjectSandbox } from '../project.sandbox';
@Component({
  selector: 'app-create-new-project',
  templateUrl: './create-new-project.component.html',
  styleUrls: ['./create-new-project.component.scss']
})

@Injectable({
  providedIn: 'root'
})
// This is a component used to display create button to redirect to create new project
export class CreateNewProjectComponent {
  constructor(public projectSandbox: ProjectSandbox, public projectsAPI: ProjectsAPI, public navSandbox: NavSandbox) { }

  createNewProject() {
    this.projectsAPI.setIsNewProjectClicked(true);
  }
}
