// tslint:disable: typedef
// tslint:disable: semicolon
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, Inject } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { MatIconRegistry } from '@angular/material/icon';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { GridApi } from 'ag-grid-community';
interface Requests {
  created: string;
  created_by: number;
  name: string;
  notifications: {
    emails: [];
    phones: [];
  };
  request: {
    method: string;
    url: string;
  };
  is_active: boolean;
  request_interval_seconds: number;
  status: string;
  timezone: string;
  tolerated_failures: number | boolean;
  updated: string;
}
interface Users {
  id: number;
  label: string;
  name: string;
  photoUrl: string;
  type: string;
}
interface Tasks {
  id: number;
  task_id: number;
  task_last_run: string;
  task_name: string;
  task_status: string;
}
@Component({
  selector: 'app-dialog-overview-example-dialog',
  templateUrl: 'view_edit.html',
  styleUrls: ['./requests.component.scss'],
})
export class View_edit_example_dialog {
  intervals: Array<{ name: string; value: number }> = [];
  response = undefined;
  constructor(
    private readonly http: HttpClient,
    public dialogRef: MatDialogRef<View_edit_example_dialog>,
    @Inject(MAT_DIALOG_DATA)
    public data: { request: Requests; add: boolean; allUsers: Users }
  ) {
    for (let i = 30; i <= 3600; i += 30) {
      this.intervals.push({ name: `${i} seconds`, value: i });
    }
    data.request.tolerated_failures = data.request.tolerated_failures > 1;
  }
  test() {
    this.http
      .post(`/api/data`, { url: this.data.request.request.url })
      .subscribe((response) => {
        this.response = response;
      });
  }
  save() {
    this.data.request.tolerated_failures = this.data.request.tolerated_failures
      ? 1
      : 3;
    this.dialogRef.close(this.data.request);
  }
  onNoClick(): void {
    this.dialogRef.close();
  }
}
@Component({
  selector: 'app-requests',
  templateUrl: './requests.component.html',
  styleUrls: ['./requests.component.scss'],
})
export class RequestsComponent implements OnInit {
  constructor(
    private readonly http: HttpClient,
    iconRegistry: MatIconRegistry,
    sanitizer: DomSanitizer,
    public dialog: MatDialog
  ) {
    iconRegistry.addSvgIcon(
      'action_pause',
      sanitizer.bypassSecurityTrustResourceUrl('/assets/action_pause.svg')
    );
  }
  requests: Array<Requests>;
  filterRequests: Array<Requests>;
  allUsers: Array<Users>;
  allTasks: Array<Tasks>;
  requestFilter = '';
  gridColumnDef = [
    { headerName: 'Task Name', field: 'task_name' },
    { headerName: 'Task Status', field: 'task_status' },
    { headerName: 'Task Last Run', field: 'task_last_run' },
  ];
  defaultColDef = {
    filter: 'agTextColumnFilter',
    sortable: true,
    resizable: true,
  };
  ngOnInit(): void {
    this.getallrequests();
    this.getallUsers();
    this.get_tasks();
  }
  get_tasks() {
    this.http.get('/api/tasks').subscribe((tasks: { data: Array<Tasks> }) => {
      this.allTasks = tasks.data;
    });
  }
  onGridReady(evt: {api: GridApi}){
    evt.api.sizeColumnsToFit()
  }
  add_request() {
    const request = {
      id: this.requests.length + 1,
      created_by: 99,
      name: '',
      notifications: {
        emails: [],
        phones: [],
      },
      request: {
        method: 'GET',
        url: '',
      },
      is_active: true,
      request_interval_seconds: 30,
      status: 'Active',
      timezone: 'GMT',
      tolerated_failures: 1,
    };
    const dialogRef = this.dialog.open(View_edit_example_dialog, {
      width: '600px',
      disableClose: true,
      data: { request, add: true, allUsers: this.allUsers },
    });
    dialogRef.afterClosed().subscribe((response: Request) => {
      if (response !== undefined) {
        this.modify_request(response);
      }
    });
  }
  view_request(request: Requests) {
    const dialogRef = this.dialog.open(View_edit_example_dialog, {
      width: '600px',
      disableClose: true,
      data: { request, add: false, allUsers: this.allUsers },
    });
    dialogRef.afterClosed().subscribe((response: Request) => {
      if (response !== undefined) {
        this.modify_request(response);
      }
    });
  }
  onFilter() {
    const searchterm = this.requestFilter.toLowerCase();
    if (searchterm === '') {
      this.filterRequests = this.requests;
    } else {
      this.filterRequests = this.requests.filter((req) =>
        req.name.toLowerCase().includes(searchterm)
      );
    }
  }
  action_request(action, request: Requests) {
    this.http.post('/api/requests/' + action, request).subscribe((_) => {
      this.getallrequests();
    });
  }

  modify_request(request) {
    this.http.post('/api/requests', request).subscribe((_) => {
      this.getallrequests();
    });
  }
  getallUsers() {
    this.http.get('/api/users').subscribe((users: { data: Array<Users> }) => {
      this.allUsers = users.data;
    });
  }
  getallrequests() {
    this.http
      .get('/api/requests')
      .subscribe((requests: { data: Array<Requests> }) => {
        this.requests = requests.data;
        if (this.requestFilter === '') {
          this.filterRequests = this.requests;
        }
      });
  }
}
