import { Component } from '@angular/core';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { THEMES } from 'src/app/shared/utils/constants';
import { addThemeSwitchClass } from 'src/app/shared/utils/utils';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  themesOption: any;
  onEnvironmentEdit = false;
  environmentData: any = [];
  constructor(public sharedAPI: SharedAPI, public projectAPI: ProjectsAPI) {
    this.themesOption = THEMES;
    this.environmentData = JSON.stringify(sharedAPI.getEnvironmentConfig(), null, '   ');
  }

  onThemeChange(value: any) {
    localStorage.setItem('selectedTheme', value.code);
    this.sharedAPI.setSelectedTheme(value);
    addThemeSwitchClass(value);
    if (value === THEMES[0] || value === THEMES[1]) {
      this.sharedAPI.setSelectedLightTheme(value);
    }
  }
}
