import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { getBaseUrl } from 'src/environments/environment';
import { getTimeStamp } from './utils/utils';

@Injectable()
export class TestRunService {
  constructor(private http: HttpClient) { }

  getRunningTestsJson(): Observable<any> {
    return this.http.get(getBaseUrl() + 'running-testcases');
  }
  getTestLogs() {
    return this.http.get(getBaseUrl() + 'test-logs');
  }
  async getTestExecutionResult(isArchived: any, projectId: any, skipLimit: any) {
    return await this.http.get(getBaseUrl() + 'test_run_executions/?archived=' + isArchived + '&project_id=' +
      projectId + '&skip=' + skipLimit + '&limit=250');
  }
  getDefaultTestCases(): Observable<any> {
    return this.http.get(getBaseUrl() + 'test_collections');
  }
  async createTestRunConfig(requestJson: any) {
    const testConfigData = await this.http.post(getBaseUrl() + 'test_run_configs', requestJson).toPromise();
    return testConfigData;
  }
  createTestRunExecution(testConfigId: number, selectedProjectId: number, testName: string, operatorId: any,
    description: any): Observable<any> {
    /* eslint-disable @typescript-eslint/naming-convention */
    const requestJson = {
      'test_run_execution_in':
      {
        'title': testName + '_' + getTimeStamp(), 'test_run_config_id': testConfigId,
        'project_id': selectedProjectId, 'description': description, 'operator_id': operatorId
      }
    };
    /* eslint-enable @typescript-eslint/naming-convention */
    return this.http.post(getBaseUrl() + 'test_run_executions', requestJson);
  }
  startTestRunExecution(id: number): Observable<any> {
    return this.http.post(getBaseUrl() + 'test_run_executions/' + id + '/start', {});
  }
  readTestRunExecution(id: number): Observable<any> {
    return this.http.get(getBaseUrl() + 'test_run_executions/' + id, {});
  }
  async readTestRunExecutionAsync(id: number) {
    return await this.http.get(getBaseUrl() + 'test_run_executions/' + id, {}).toPromise();
  }
  abortTestExecution(): Observable<any> {
    return this.http.post(getBaseUrl() + 'test_run_executions/abort-testing', {});
  }
  getOperatorData() {
    return this.http.get(getBaseUrl() + 'operators/');
  }
  setOperatorData(operator: any) {
    return this.http.post(getBaseUrl() + 'operators', { 'name': operator });

  }
  deleteOperator(operator: any) {
    return this.http.delete(getBaseUrl() + 'operators/' + operator.id);
  }
  updateOperator(data: any) {
    return this.http.put(getBaseUrl() + 'operators/' + data.id, { 'name': data.name });
  }
  archiveTestRun(id: any) {
    return this.http.post(getBaseUrl() + 'test_run_executions/' + id + '/archive', {});
  }
  unarchiveTestRun(id: any) {
    return this.http.post(getBaseUrl() + 'test_run_executions/' + id + '/unarchive', {});
  }
  deleteTestRun(id: any) {
    return this.http.delete(getBaseUrl() + 'test_run_executions/' + id);
  }
  searchTestExecutionHistory(searchQuery: any, isArchived: any, projectId: any) {
    return this.http.get(getBaseUrl() + 'test_run_executions/?archived=' + isArchived +
      '&project_id=' + projectId + '&search_query=' + searchQuery);
  }
  fileUpload(data: File) {
    // eslint-disable-next-line prefer-const
    let formData: FormData = new FormData();
    formData.append('file', data, data.name);
    return this.http.post(getBaseUrl() + 'test_run_executions/file_upload/', formData);
  }
  getLogs(logId: any, json: any) {
    return this.http.get(getBaseUrl() + 'test_run_executions/' + logId + '/log?json_entries=' + json, { responseType: 'text' });
  }
  getApplicableTestCases(data: any) {
    return this.http.get(getBaseUrl() + 'projects/' + data + '/applicable_test_cases');
  }

  async getExecutionStatus() {
    return await this.http.get(getBaseUrl() + 'test_run_executions/status').toPromise();
  }
  importTestRun(file: File, projectId: number) {
    const formData: FormData = new FormData();
    formData.append('import_file', file, file.name);
    return this.http.post(getBaseUrl() + `test_run_executions/import?project_id=${projectId}`, formData);
  }
  exportTestRun(data: any, download: boolean) {
    return this.http.get(getBaseUrl() + `test_run_executions/${data.id}/export?download=${download}`);
  }
}
