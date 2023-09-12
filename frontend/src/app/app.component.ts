import { AfterViewInit, Component } from '@angular/core';
import { MainAreaSandbox } from './components/main-area/main-area.sandbox';
import { ProjectsAPI } from './shared/core_apis/project';
import { SharedService } from './shared/core_apis/shared-utils';
import { DataService } from './shared/web_sockets/ws-config';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent implements AfterViewInit {
  constructor(public projectsAPI: ProjectsAPI, private dataService: DataService, public mainAreaSandbox: MainAreaSandbox,
    public sharedService: SharedService) {
    mainAreaSandbox.syncDataToServer(this.dataService);
  }
  ngAfterViewInit() {
    this.sharedService.checkBrowserAndVersion();
  }
}
