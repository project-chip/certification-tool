import { Injectable } from '@angular/core';
import { ProjectsAPI } from 'src/app/shared/core_apis/project';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { WebSocketAPI } from 'src/app/shared/core_apis/websocket';
import { APP_STATE } from 'src/app/shared/utils/constants';
import { ProjectStore } from '../../store/project-store';
import { ProjectSandbox } from '../project/project.sandbox';
import { TestSandbox } from '../test/test.sandbox';
@Injectable()
export class MainAreaSandbox {
  index = -1;
  constructor(public projectStore: ProjectStore, public testRunAPI: TestRunAPI, public projectsAPI: ProjectsAPI,
    public testSandBox: TestSandbox, public sharedAPI: SharedAPI, public projectSandbox: ProjectSandbox,
    public webSocketAPI: WebSocketAPI) {
    testRunAPI.getDefaultTestCases(this.getTestData.bind(this));
  }
  public fetchCurrentIndex() {
    this.index = this.projectStore.currentPanelIndex;
    return this.index;
  }

  getTestData() {
    this.testSandBox.getTestData();
  }

  async syncDataToServer(dataService: any) {
    await dataService.connect();
    await this.webSocketAPI.socketSubscription();
    await this.projectsAPI.getAllProjectData(false);
    this.projectsAPI.getAllProjectData(true);
    const testExecStatusData: any = await this.testRunAPI.getExecutionStatus();

    if (testExecStatusData.state === 'running') {
      this.sharedAPI.setAppState(APP_STATE[1]);
      await this.testRunAPI.readRunningTestsRawDataAsync(testExecStatusData.test_run_execution_id,
        this.testRunAPI.updateRunningTestcase.bind(this.testRunAPI));

      this.sharedAPI.setExecutionStatus(testExecStatusData);  //  update exexutionStatus after completing above api. (used for rendering)

      const testRundata: any = this.testRunAPI.getRunningTestCasesRawData();
      const allProjects = this.projectSandbox.getAllProjectData();
      const currentProject = allProjects.filter((ele: any) => ele.id === testRundata.project_id);
      this.sharedAPI.setSelectedProjectType(currentProject[0]);
      this.projectsAPI.setCurrentPanelIndex(1);
      this.testSandBox.setTestScreen(1);

    } else {
      this.sharedAPI.setExecutionStatus(testExecStatusData);
    }
  }
}
