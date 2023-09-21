import { AfterViewInit, Component } from '@angular/core';
import { TestRunAPI } from 'src/app/shared/core_apis/test-run';
import { TestSandbox } from '../test.sandbox';
import * as _ from 'lodash';
@Component({
  selector: 'app-test-operator',
  templateUrl: './test-operator.component.html',
  styleUrls: ['./test-operator.component.scss']
})
export class TestOperatorComponent implements AfterViewInit {
  addNew = false;
  filteredOperator?: any = [];
  selectedOperator?: any;
  warning = false;
  operatorEdit = false;
  operatorData: any = '';
  allowedCharacter = /[^A-Za-z0-9 _-]/;

  constructor(public testSandbox: TestSandbox, public testRunAPI: TestRunAPI) {
    this.selectedOperator = testRunAPI.getSelectedOperator();
  }

  ngAfterViewInit() {
    this.blockCopyPasteForOperator();
  }

  // This function will not let user to copy, cut, paste the operator name
  blockCopyPasteForOperator() {
    const inputBox = document.querySelector('#autoc input') as HTMLButtonElement;
    if (inputBox) {
      ['paste', 'copy', 'cut'].forEach(eventType =>
        inputBox.addEventListener(eventType, (e) => {
          e.preventDefault();
        })
      );
    }
  }

  // filter operator data
  onFilterOperator(event: any) {
    let filteredData: any = [];
    this.addNew = false;
    this.warning = false;
    const operators = _.cloneDeep(this.testSandbox.getOperatorData());
    let query = event.query;
    if (query) {
      if (this.allowedCharacter.test(query)) {
        const regex = new RegExp(this.allowedCharacter, 'g');
        query = query.replace(regex, '');
        this.selectedOperator = { name: query };
      }
      for (let i = 0; i < operators.length; i++) {
        const operator = operators[i];
        if (operator.name.toLowerCase().indexOf(query.toLowerCase()) === 0) {
          filteredData.push(operator);
        }
      }
      if (filteredData.length === 0) {
        filteredData = [{ name: query }];
        this.addNew = true;
      }
      this.filteredOperator = filteredData;
    } else {
      this.filteredOperator = _.cloneDeep(this.testSandbox.getOperatorData());
    }

  }

  // add new operator
  addNewOperator(newOperator: any) {
    this.testSandbox.setOperatorData(newOperator, (data: any) => {
      this.testRunAPI.setSelectedOperator(data);
    });
  }

  // delete operator
  deleteOperator(operator: any) {
    this.testSandbox.deleteOperator(operator);
    this.testRunAPI.setSelectedOperator('');
    this.selectedOperator = '';
  }

  // When user select operator
  onSelectedOperator(operator: any) {
    this.testRunAPI.setSelectedOperator(operator);
  }
  isString(value: any) {
    return typeof value === 'string';
  }
  editOperator(data: any) {
    this.operatorData = data;
    this.operatorEdit = true;
  }
  updateOperator() {
    this.testSandbox.updateOperator(this.operatorData);
    this.operatorEdit = false;
  }
}
