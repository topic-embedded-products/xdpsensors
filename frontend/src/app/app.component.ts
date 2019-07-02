import { Component, OnInit } from '@angular/core';
import {Observable} from 'rxjs/Rx';
import { BackendService } from './backend.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  title = 'drone-frontend';
  private sensorData: Observable<any>

  constructor(private backend: BackendService) {

  }
  
  ngOnInit(): void {
    this.getSensorData();
  }

  getSensorData(){
    console.log("it is in getsensordata")
    this.sensorData = this.backend.getSensorData()
  }
}
