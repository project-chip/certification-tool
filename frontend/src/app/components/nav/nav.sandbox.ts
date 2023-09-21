import { Injectable } from '@angular/core';
import { ProjectStore } from '../../store/project-store';

@Injectable()
export class NavSandbox {
  public currentIndex: any;
  constructor(private projectStore: ProjectStore) { }

  public getCurrentIndex() {
    this.currentIndex = this.projectStore.currentPanelIndex;
    return this.currentIndex;
  }

  public getIsNewProjectClicked() {
    return this.projectStore.isNewProjectClicked;
  }
}
