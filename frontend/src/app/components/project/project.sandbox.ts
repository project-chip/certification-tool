import { Injectable } from '@angular/core';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { ProjectStore } from '../../store/project-store';

@Injectable()
export class ProjectSandbox {
  public isNewProjectClicked: any;
  public newProjectDetails: any;
  constructor(private projectStore: ProjectStore, private projectsAPI: ProjectsAPI) { }

  public getNewProjectDetails() {
    this.newProjectDetails = this.projectStore.newProjectDetails;
    return this.newProjectDetails;
  }
  public getIsNewProjectClicked() {
    this.isNewProjectClicked = this.projectStore.isNewProjectClicked;
    return this.isNewProjectClicked;
  }
  public createNewProject() {
    const projectDetails = this.projectsAPI.getProjectDetails();
    /* eslint-disable @typescript-eslint/naming-convention */
    const requestData = {
      'name': projectDetails.name,
      'config': projectDetails.config

    };
    /* eslint-enable @typescript-eslint/naming-convention */
    this.projectsAPI.setProjectData(requestData);
  }
  getAllProjectData() {
    return this.projectStore.allProjectData;
  }
  deleteProject(projectId: number) {
    this.projectsAPI.deleteProject(projectId);
  }
  getArchivedProjects() {
    return this.projectStore.archivedProjects;
  }
  getProjectType() {
    return this.projectStore.projectType;
  }
  setProjectType(data: any) {
    this.projectStore.setProjectType(data);
  }
}
