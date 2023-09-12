import { Component, Injectable, OnInit } from '@angular/core';
import { getDefaultSettings, ProjectsAPI } from 'src/app/shared/core_apis/project';
import { ProjectService } from 'src/app/shared/project-utils';
import { ProjectSandbox } from '../project.sandbox';

@Component({
  selector: 'app-device-detail-list',
  templateUrl: './device-detail-list.component.html',
  styleUrls: ['./device-detail-list.component.scss']
})

@Injectable()
// This component is wrapping the device-details and show additional config
export class DeviceDetailListComponent implements OnInit {
  addedSettings: any[];
  settingsType: any[];

  constructor(public projectsAPI: ProjectsAPI, public projectSandbox: ProjectSandbox, public projectService: ProjectService) {
    this.addedSettings = getDefaultSettings();
    this.settingsType = getDefaultSettings();
  }

  ngOnInit() {
    this.projectsAPI.getSettingsJsonData();
  }
  onCreate() {
    if (!this.projectsAPI.getIsCreateProjectContainsWarning()) {
      this.projectService.cursorBusy(true);
      this.projectSandbox.createNewProject();
    }
  }
}
