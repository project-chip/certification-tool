/* eslint-disable @typescript-eslint/no-use-before-define */
/* eslint-disable no-use-before-define */
import { Injectable } from '@angular/core';
import { ProjectService } from '../project-utils';
import { ProjectStore } from 'src/app/store/project-store';
import { SharedService } from './shared-utils';
import { SharedStore } from 'src/app/store/shared-store';
import { Title } from '@angular/platform-browser';

@Injectable()
export class ProjectsAPI {
  public projectData: any;
  public runningTestCases: any;
  archivedLimit = 0; unArchivedLimit = 0; setArchived = false;
  archivedData: any = []; unArchivedData: any = []; setUnarchived = false;
  constructor(private projectService: ProjectService, private projectStore: ProjectStore,
    private sharedService: SharedService, private sharedStore: SharedStore, private titleService: Title) {
    this.getEnvironmentConfig();
    this.getShaVersion();
  }
  getProjectData() {
    this.projectData = this.projectStore.allProjectData;
    return this.projectData;
  }
  getRunningTestCases() {
    this.runningTestCases = this.projectStore.runningTestCases;
    return this.runningTestCases;
  }
  getProjectDetails() {
    return this.projectStore.projectDetails;
  }
  setProjectDetails(value: any) {
    this.projectStore.setProjectDetails(value);
  }
  setIsNewProjectClicked(value: boolean) {
    this.projectStore.setIsNewProjectClicked(value);
  }
  setCurrentPanelIndex(value: number) {
    this.projectStore.setCurrentPanelIndex(value);
  }
  setUserIndex(data: number) {
    this.projectStore.setUserIndex(data);
  }

  getIsCreateProjectContainsWarning() {
    return this.projectStore.isCreateProjectContainsWarning;
  }
  setIsCreateProjectContainsWarning(value: boolean) {
    this.projectStore.setIsCreateProjectContainsWarning(value);
  }

  getSettingsJsonData() {
    return this.projectService.getSettingsJson().subscribe(
      (data) => {
        this.projectStore.setNewProjectDetails(data);
        return data;
      });
  }
  getDataLimit(data: any) {
    if (data) {
      return this.archivedLimit;
    } else {
      return this.unArchivedLimit;
    }
  }
  getAllProjectData(isArchived: any) {
    return this.projectService.getProjectData(isArchived, this.getDataLimit(isArchived)).subscribe(
      (data) => {
        if (isArchived) {
          if (data.length >= 250) {
            this.archivedData.push(...data);
            this.archivedLimit += 250;
            this.getAllProjectData(isArchived);
          } else {
            this.archivedData.push(...data);
            this.projectStore.setArchivedProjects(this.archivedData);
            this.archivedData = [];
            this.archivedLimit = 0;
            this.setArchived = true;
            this.checkProjectData();
          }
        } else {
          if (data.length >= 250) {
            this.unArchivedData.push(...data);
            this.unArchivedLimit += 250;
            this.getAllProjectData(isArchived);
          } else {
            this.unArchivedData.push(...data);
            this.projectStore.setAllProjectData(this.unArchivedData.reverse());
            this.projectStore.setIsNewProjectClicked(false);
            this.unArchivedData = [];
            this.unArchivedLimit = 0;
            this.setUnarchived = true;
            this.checkProjectData();
          }
        }
        return data;
      }, err => {
        this.sharedService.showPopUp();
      });
  }
  checkProjectData() {
    if (this.setArchived && this.setUnarchived) {
      if (this.projectStore.allProjectData.length) {
        this.projectStore.setProjectType(projectDropdown()[0]);
        this.projectStore.setCurrentPanelIndex(4);
      } else if (this.projectStore.archivedProjects.length) {
        this.projectStore.setProjectType(projectDropdown()[1]);
        this.projectStore.setCurrentPanelIndex(4);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'No Active project found' });
      }
      this.setArchived = false; this.setUnarchived = false;
    }
  }
  setProjectData(value: any) {
    return this.projectService.setProjectData(value).subscribe(
      (data: any) => {
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Project added successfully.' });
        this.getAllProjectData(false);
        this.getAllProjectData(true);
        this.projectService.cursorBusy(false);
        return data;
      }, err => {
        this.projectService.cursorBusy(false);
        this.sharedService.showPopUp();
      });
  }
  deleteProject(projectId: number) {
    this.projectService.deleteProject(projectId).subscribe(
      (data: any) => {
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Project deleted successfully.' });
        this.getAllProjectData(false);
        return data;
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error occured in deleting project.' });
      }
    );
  }

  updateProject(data: any) {
    this.projectService.updateProject(data).subscribe(
      (updatedData: any) => {
        this.getAllProjectData(false);
        this.getAllProjectData(true);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Project Updated successfully.' });
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in updating Project.' });
      }
    );
  }

  archiveProject(id: any) {
    this.projectService.archiveProject(id).subscribe(
      (data: any) => {
        this.getAllProjectData(false);
        this.getAllProjectData(true);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Project archived successfully.' });
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in archive Project..' });
      }
    );
  }

  unarchiveProject(id: any) {
    this.projectService.unarchiveProject(id).subscribe(
      (data: any) => {
        this.getAllProjectData(false);
        this.getAllProjectData(true);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'Project unarchived successfully.' });
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in unarchive Project..' });
      }
    );
  }
  getEnvironmentConfig() {
    this.projectService.getEnvironmentConfig().subscribe(
      (data: any) => {
        this.sharedStore.setEnvironmentConfig(data);
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Unprocessable Entity' });
      }
    );
  }
  uploadPics(data: any, id: any, picsCallback: any, picsUpdate: any) {
    this.projectService.uploadPics(data, id).subscribe(
      (e: any) => {
        picsCallback();
        picsUpdate(e);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'PICS Uploaded successfully.' });
      }, err => {
        picsCallback();
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in uploading PICS.' });
      }
    );
  }
  deletePics(data: any, id: any, callback: any) {
    this.projectService.deletePics(data, id).subscribe(
      (e: any) => {
        callback(e);
        this.sharedService.setToastAndNotification({ status: 'success', summary: 'Success!', message: 'PICS deleted successfully.' });
      }, err => {
        this.sharedService.setToastAndNotification({ status: 'error', summary: 'Error!', message: 'Error in deleting PICS.' });
      }
    );
  }
  getShaVersion() {
    this.projectService.getShaVersion().subscribe(
      (data: any) => {
        this.titleService.setTitle('Matter Test Harness (' + data.version + ')');
        this.sharedStore.setShaVersion(data);
      }
    );
  }
}


// Return default added values
export function getDefaultSettings() {
  const addedSettings = [
    { name: 'Wi-Fi', code: 'wifi' },
    { name: 'Internet Protocol', code: 'ip' },
  ];
  return addedSettings;
}
export function projectDropdown() {
  const projectDropdownData = [
    {
      tableName: 'Projects',
      toolTip: 'Archive'
    },
    {
      tableName: 'Archive Project',
      toolTip: 'Unarchive'
    },
  ];
  return projectDropdownData;
}
