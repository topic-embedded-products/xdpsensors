import { Component, OnInit } from '@angular/core';
import {Observable} from 'rxjs/Rx';
import { BackendService, BME680, AMS, BMI088_ACCEL, BMI088_GYRO } from './backend.service';
import 'rxjs/add/operator/map'
import { Subscription, timer, pipe, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import {MatSliderChange} from '@angular/material'

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent implements OnInit {

  title = 'drone-frontend';
  private sensorData: Observable<any>
  private bme: BME680[];
  private ams: AMS[];
  private bmi088_accel: BMI088_ACCEL[];
  private bmi088_gyro: BMI088_GYRO[];
  bme680_subscription: Subscription;
  ams_subscription: Subscription;
  bmi088_accel_subscription: Subscription;
  bmi088_gyro_subscription: Subscription;
  motorSpeed = 50;
  constructor(private backend: BackendService) {
  }
  
  ngOnInit(): void {
    this.bme680_subscription = timer(0, 1000).pipe(
      switchMap(() => this.backend.getSensorData<BME680[]>("bme680"))
    ).subscribe(result => this.bme = result);
    this.ams_subscription = timer(0, 1000).pipe(
      switchMap(() => this.backend.getSensorData<AMS[]>("ams"))
    ).subscribe(result => this.ams = result);
    this.bmi088_accel_subscription = timer(0, 1000).pipe(
      switchMap(() => this.backend.getSensorData<BMI088_ACCEL[]>("bmi088_accel"))
    ).subscribe(result => this.bmi088_accel = result);
    this.bmi088_gyro_subscription = timer(0, 1000).pipe(
      switchMap(() => this.backend.getSensorData<BMI088_GYRO[]>("bmi088_gyro"))
    ).subscribe(result => this.bmi088_gyro = result);
  }

  ngOnDestroy() {
    this.bme680_subscription.unsubscribe();
    this.ams_subscription.unsubscribe();
    this.bmi088_accel_subscription.unsubscribe();
    this.bmi088_gyro_subscription.unsubscribe();
}

  getString(obj : any){
    return JSON.stringify(obj);
  }
  getSensorData(){
    this.backend.getSensorData<BME680[]>("bme680")
    .subscribe(
      data => {
        this.bme = data
        //console.log(this.bme)
      }
    )

    this.backend.getSensorData<any>("ams")
    .subscribe(
      (data : AMS[]) => {
        this.ams = data
        //console.log(JSON.stringify(this.ams))
      }
    )

    this.backend.getSensorData<BMI088_ACCEL[]>("bmi088_accel")
    .subscribe(
      data => {
        this.bmi088_accel = data
        //console.log(this.bmi_accel)
      }
    )

    this.backend.getSensorData<BMI088_GYRO[]>("bmi088_gyro")
    .subscribe(
      data => {
        this.bmi088_gyro = data
        //console.log(this.bmi_gyro)
      }
    )
  }

  onInputChange(event: MatSliderChange) {
    this.motorSpeed = event.value;
  }


}

