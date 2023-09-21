import { Component } from '@angular/core';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { SharedAPI } from 'src/app/shared/core_apis/shared';


@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.scss']
})

// This component used to display input for project details
export class ProjectDetailsComponent {
  // projectTypes: ProjectType[];
  // selectedProjectType: ProjectType;
  selectedTransport: string[] = [];
  allowedCharacter = /[^A-Za-z0-9 _-]/;
  projectName = 'New Project';
  onEnvironmentEdit = false;
  environmentData: any = [];
  constructor(public projectsAPI: ProjectsAPI, public sharedAPI: SharedAPI) {
    this.environmentData = JSON.stringify(sharedAPI.getEnvironmentConfig(), null, '   ');
    const projectDetails = this.projectsAPI.getProjectDetails();
    projectDetails.config = JSON.parse(this.environmentData);
    this.projectsAPI.setProjectDetails(projectDetails);
  }
  onProjectNameChange(event: any) {
    const query = event.target.value;
    this.projectsAPI.setIsCreateProjectContainsWarning(false);
    if (this.allowedCharacter.test(query) || query === '') {
      this.projectsAPI.setIsCreateProjectContainsWarning(true);
      this.projectName = query;
    }
    const projectDetails = this.projectsAPI.getProjectDetails();
    projectDetails.name = query;
    this.projectsAPI.setProjectDetails(projectDetails);
  }

  jsonToHtml(data: any) {
    data = data.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    data = data.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      function (match: any) {
        let cls = 'number';
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'key';
          } else {
            cls = 'string';
          }
        } else if (/true|false/.test(match)) {
          cls = 'boolean';
        } else if (/null/.test(match)) {
          cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
      });

    return data;

  }
  updateEnvironment() {
    const projectDetails = this.projectsAPI.getProjectDetails();
    projectDetails.config = JSON.parse(this.environmentData);
    this.projectsAPI.setProjectDetails(projectDetails);
    this.onEnvironmentEdit = false;
  }
}
