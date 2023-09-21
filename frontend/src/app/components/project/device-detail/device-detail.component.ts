import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-device-detail',
  templateUrl: './device-detail.component.html',
  styleUrls: ['./device-detail.component.scss']
})

// This component will loop through selected settings and display the UI inputs
export class DeviceDetailComponent {
  @Input() addedSetting: any;
  @Input() settingsType: any;
  @Input() settingsJson: any;

  getValue(data: any) {
    return data.value;
  }

  getType(data: any) {
    return data.type;
  }

  unsorted() {
    return 1;
  }
}
