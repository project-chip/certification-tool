import { DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { SharedAPI } from 'src/app/shared/core_apis/shared';
import { MainAreaSandbox } from '../main-area/main-area.sandbox';

@Component({
  selector: 'app-utility',
  templateUrl: './utility.component.html',
  styleUrls: ['./utility.component.scss']
})
export class UtilityComponent {
  testHistory: any = '';
  millis = 0;
  statisticsData: any;
  data: any = '';
  tableFields = [
    { name: 'Description', id: 1 },
    { name: 'Time Elapsed', id: 2 },
    { name: 'Title', id: 3 }
  ];
  selectedFields: any = [
    { name: 'Time Elapsed', id: 2 }
  ];
  constructor(public sharedAPI: SharedAPI, public mainAreaSandbox: MainAreaSandbox, public date: DatePipe) {
    sharedAPI.setTestReportData('');
  }
  // find Time Elapsed
  getTimeDifference(start: any, end: any) {
    this.millis = new Date(end).getTime() - new Date(start).getTime();
    if (!end || !start) {
      return '-';
    }
    let minutes = 0, seconds = 0;
    if (this.millis > 0) {
      minutes = this.millis / 60000;
      seconds = (this.millis % 60000) / 1000;
    }
    return Math.floor(minutes) + 'm' + Math.floor(seconds) + 's';
  }
  // returns time
  getTime(date: any) {
    if (date) {
      const time = date.replace(/-/g, '/').replace(/\.(.*[0-9])/g, '').split('T');
      const timeZone = new Date(time[0] + ' PST').toUTCString();
      if (timeZone.includes('08:00:00 GMT')) {
        date = time[0] + ' ' + time[1] + ' PDT';
      } else {
        date = time[0] + ' ' + time[1] + ' PST';
      }
      return new Date(date);
    } else {
      return NaN;
    }
  }
  // filter columns
  isFieldDisplayed(id: any) {
    let isDisplay = 0;
    this.selectedFields.forEach((data: any) => {
      if (data.id === id) {
        isDisplay = 1;
      }
    });
    if (isDisplay) {
      return false;
    } else {
      return true;
    }
  }
  reportStatistics() {
    const statistics: any = { 'pending': 0, 'error': 0, 'cancelled': 0, 'failed': 0, 'passed': 0 };
    const states: any = {};
    let percent = 0, toalCase = 0;
    this.sharedAPI.getTestReportData().test_suite_executions.forEach((data: any) => {
      data.test_case_executions.forEach((testCases: any) => {
        statistics[testCases.state]++;
        toalCase++;
      });
    });
    if (toalCase > 0) {
      percent = 100 / toalCase;
    }
    states['passed'] = (statistics.passed || 0) * percent;
    states['failed'] = (statistics.failed || 0) * percent + states.passed;
    states['error'] = (statistics.error || 0) * percent + states.failed;
    states['cancelled'] = (statistics.cancelled || 0) * percent + states.error;
    states['pending'] = (statistics.pending || 0) * percent + states.cancelled;
    const final = '--percent-passed:' + states.passed + '%; --percent-failed:' + states.failed + '%; --percent-error:'
      + states.error + '%; --percent-cancelled:' + states.cancelled + '%; --percent-pending:' + states.pending + '%;';
    this.statisticsData = statistics;
    return final;
  }
  /* eslint-disable prefer-const */
  // Print report
  printDoc() {
    let printContents, popupWin;
    printContents = document.getElementById('print-section')?.innerHTML;
    let operator = 'Unknown';
    if (this.sharedAPI.getTestReportData().operator) {
      operator = this.sharedAPI.getTestReportData().operator.name;
    }
    popupWin = window.open('');
    popupWin?.document.open();
    popupWin?.document.write(` 
      <html> 
        <head>
          <title>Test Report</title>
          <style>
     
          .test-report {
            margin: 13px;
            height: calc(100vh - 274px);
            overflow: auto;
          }
          .test-border,.utility-parent{
            border:1px solid #e3e1e187;
            box-shadow: 0px 6px 12px 3px rgb(0 0 0 / 10%);
          
          }
          .data-table {
            table-layout: fixed;
            }
          table,
          th,
          td {
            border: 1px solid #c3bfbf;
            border-collapse: collapse;
          }
          th {
            background-color: #eeebf047;
          }
          .error {
            color: red;
          }
          .passed {
            color: green;
          }
          .pending{
            color: orange;
          }
          
          .report-title {
            text-align: left;
          }
          .detail-divider,
          .detail-summary {
            border-top: 2px solid rgba(151, 151, 151, 0.849);
            margin: 0 0 18px 0;
          }
          
          .detail-summary {
            margin-bottom: 0;
          }
          .test-case {
            padding-left: 22px !important;
          }
          .test-step {
            padding-left: 37px !important;
          }
          .report-heading{
            width: 90vw;
          }
          .report-detail,
          .report-summary {
            width: 90vw;
          }
            table {
              width: 100%;
              margin-bottom: 20px;
            }
              tr{
                line-height: 35px;
              }
              th,td{
                text-align: left;
                padding: 0 6px 0 6px;
              }
            
          
          
            .report-detail  .test-run{
              padding:10px 35px 1px 35px;
              border: 1px solid #c3bfbf;
            }
            .report-detail  .test-title{
              font-size: 12px;
            }
            .report-detail  .bold-test-title{
              font-weight: 400;
            }
          
          .bold-title {
            font-weight: bold;
          }
          .loader-div {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
          }
          
          .utility-parent{
            margin: 8px;
          }
        .d-none, .custom-select, .print-button{
          display: none;
        }     
        
        .text-warp, .Not_applicable {
          line-break:anywhere;
        }
.statistics {
  width: 90vw;
}
  .statistics-bar {
    border: 1px solid #c3bfbf;
    height: 75px;
  }
  .progress-bar-legends {
    text-align: center;
  }
    .progress-bar-text {
      margin-right: 25px;
    }
    .progress-bar-text span {
        color: grey;
      }
    
    .circle {
      height: 8px;
      width: 8px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 5px;
    }
  
  .progress-bar {
    width: 70%;
    height: 15px;
    border: 1px solid #c3bfbf;
    border-radius: 7px;
    margin: 17px auto;
    background-image: linear-gradient(#007e33, #007e33),
      linear-gradient(#cc0000, #cc0000), linear-gradient(#ffc933, #ffc933),
      linear-gradient(#ff8800, #ff8800), linear-gradient(#2193f6, #2193f6),
      linear-gradient(rgb(218, 209, 209), rgb(218, 209, 209));
    background-repeat: no-repeat;
    background-size: var(--percent-passed) 100%, var(--percent-failed) 100%,
      var(--percent-error) 100%, var(--percent-cancelled) 100%,
      var(--percent-pending) 100%, 100% 100%;
  }
  .error-background {
    background: #ffc933;
  }
  .passed-background {
    background: #007e33;
  }
  .pending-background {
    background: #2193f6;
  }
  .failed-background {
    background: #cc0000;
  }
  .cancelled-background {
    background: #ff8800;
  }

          </style>
        </head>
    <body onload="window.print()"><div class="report-heading" fxLayout fxLayoutAlign="space-between center">
    <h3 class="report-title">Matter Test Harness - Test Run Report</h3>
    
  </div>  
  <div class="report-detail">
  <h3 class="detail-title">Test Run Information</h3>
  <table class="data-table">
  <tr>
  <th>Test Name</th>
  <th>Status</th>
  <th>Date</th>
  <th>Time</th>
  <th>Operator</th>
  </tr>
  <tr>
  <td style="font-size: 13px; line-break:anywhere;">${this.sharedAPI.getTestReportData().title}</td>
  <td class="${this.sharedAPI.getTestReportData().state}">${this.sharedAPI.getTestReportData().state}</td>
  <td style="font-size: 13px;">${this.date.transform(this.sharedAPI.getTestReportData().started_at, 'mediumDate')}</td>
  <td>${this.date.transform(this.sharedAPI.getTestReportData().started_at, 'H:m:s')} - 
  ${this.date.transform(this.sharedAPI.getTestReportData().started_at, 'H:m:s')} 
  (${this.getTimeDifference(this.sharedAPI.getTestReportData().started_at, this.sharedAPI.getTestReportData().completed_at)})</td>
  <td>${operator}</td>
  </tr>
  </table>
  </div>
   ${printContents}</body>
      </html>`
    );
    popupWin?.document.close();
  }


}
