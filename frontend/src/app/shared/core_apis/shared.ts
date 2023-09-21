import { Injectable } from '@angular/core';
import { SharedStore } from 'src/app/store/shared-store';

@Injectable()
export class SharedAPI {
  constructor(private sharedStore: SharedStore) { }

  getShowCustomPopup() {
    return this.sharedStore.showCustomPopup;
  }
  setShowCustomPopup(value: string) {
    return this.sharedStore.setShowCustomPopup(value);
  }

  getCustomPopupData() {
    return this.sharedStore.customPopupData;
  }
  setCustomPopupData(value: any) {
    return this.sharedStore.setCustomPopupData(value);
  }

  getAppState() {
    return this.sharedStore.appState;
  }
  setAppState(value: string) {
    return this.sharedStore.setAppState(value);
  }
  setIsProjectTypeSelected(data: number) {
    this.sharedStore.setIsProjectTypeSelected(data);
  }
  getIsProjectTypeSelected() {
    return this.sharedStore.isProjecTypeSelected;
  }
  setSelectedProjectType(selectedType: any) {
    this.sharedStore.setSelectedProjectType(selectedType);

  }
  getSelectedProjectType() {
    return this.sharedStore.selectedProjectType;
  }
  setTestReportData(report: any) {
    this.sharedStore.setTestReportData(report);
  }
  getTestReportData() {
    return this.sharedStore.testReportData;
  }
  getSelectedTheme() {
    return this.sharedStore.selectedTheme;
  }
  setSelectedTheme(selectedTheme: any) {
    this.sharedStore.setSelectedTheme(selectedTheme);
  }
  getSelectedLightTheme() {
    return this.sharedStore.selectedLightTheme;
  }
  setSelectedLightTheme(selectedLightTheme: any) {
    this.sharedStore.setSelectedLightTheme(selectedLightTheme);
  }
  setNotificationMessage(data: any) {
    this.sharedStore.setNotificationMessage(data);
  }
  getNotificationMessage() {
    return this.sharedStore.notificationMessage;
  }
  setWebSocketLoader(data: any) {
    this.sharedStore.setWebSocketLoader(data);
  }

  getWebSocketLoader() {
    return this.sharedStore.webSocketLoader;
  }
  getExecutionStatus() {
    return this.sharedStore.executionStatus;
  }
  setExecutionStatus(data: any) {
    this.sharedStore.setExecutionStatus(data);
  }
  getbufferWSData() {
    return this.sharedStore.bufferWSData;
  }
  setbufferWSData(data: any) {
    this.sharedStore.setbufferWSData(data);
  }
  getTestExecutionLoader() {
    return this.sharedStore.testExecutionLoader;
  }
  setTestExecutionLoader(data: any) {
    this.sharedStore.setTestExecutionLoader(data);
  }
  getTestCaseLoader() {
    return this.sharedStore.testCaseLoader;
  }
  setTestCaseLoader(data: any) {
    this.sharedStore.setTestCaseLoader(data);
  }
  getIsNotificationRead() {
    return this.sharedStore.isNotificationRead;
  }
  setIsNotificationRead(data: any) {
    this.sharedStore.setIsNotificationRead(data);
  }
  getEnvironmentConfig() {
    return this.sharedStore.environmentConfig;
  }
  getShaVersion() {
    return this.sharedStore.shaVersion;
  }
}
