import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { BackendService, BME680, AMS, BMI088_ACCEL, BMI088_GYRO } from './backend.service';
import 'rxjs/add/operator/map'
import { Subscription, timer, pipe, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { MatSliderChange } from '@angular/material'
import { Chart } from 'chart.js';
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
  private bmi088_accel: BMI088_ACCEL;
  private bmi088_gyro: BMI088_GYRO;

  bme680_subscription: Subscription;
  ams_subscription: Subscription;
  bmi088_accel_subscription: Subscription;
  bmi088_gyro_subscription: Subscription;
  subInterval = 1000; //ms
  motorSpeed_accel = 50;
  motorSpeed_gyro = 50;


  @ViewChild("accelChart", { static: false })
  public refAccelChart: ElementRef;
  public accelChartData: any = {};
  private accelChart: Chart;

  @ViewChild("gyroChart", { static: false })
  public refGyroChart: ElementRef;
  public gyroChartData: any = {};
  private gyroChart: Chart;

  constructor(private backend: BackendService) {
    this.accelChartData = {};
    this.gyroChartData = {};
  }

  ngOnInit(): void {
    this.bme680_subscription = timer(0, this.subInterval).pipe(
      switchMap(() => this.backend.getSensorData<BME680[]>("bme680"))
    ).subscribe(result => this.bme = result);

    this.ams_subscription = timer(0, this.subInterval).pipe(
      switchMap(() => this.backend.getSensorData<AMS[]>("ams"))
    ).subscribe(result => this.ams = result);

    this.bmi088_accel_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BMI088_ACCEL>("bmi088_accel")))
      .subscribe(result => {
        this.bmi088_accel = result;
        this.chartAccelUpdate();
      });

    this.bmi088_gyro_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BMI088_GYRO>("bmi088_gyro")))
      .subscribe(result => {
        this.bmi088_gyro = result;
        this.chartGyroUpdate();
      });

    this.accelChartData = {
      labels: ["Accel x", "Accel y", "Accel z"],
      datasets: [{
        //label: '# of Votes',
        data: [0, 0, 0],
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)'
        ],
        borderWidth: 1
      }]
    };

    this.gyroChartData = {
      labels: ["Gyro x", "Gyro y", "Gyro z"],
      datasets: [{
        //label: '# of Votes',
        data: [0, 0, 0],
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)'
        ],
        borderWidth: 1
      }]
    };
  }

  ngOnDestroy() {
    this.bme680_subscription.unsubscribe();
    this.ams_subscription.unsubscribe();
    this.bmi088_accel_subscription.unsubscribe();
    this.bmi088_gyro_subscription.unsubscribe();
  }

  public ngAfterViewInit() {
    let chart = this.refAccelChart.nativeElement;
    let ctx = chart.getContext("2d");
    this.accelChart = new Chart(ctx, {
      type: 'bar',
      data: this.accelChartData,
      options: {
        scales: {
          yAxes: [{
            ticks: {
              suggestedMin: -360,
              suggestedMax: 360
            }
          }]
        },
        legend: { display: false },
        tooltips: { enabled: false },
        hover: { mode: null }
      }
    });

    chart = this.refGyroChart.nativeElement;
    ctx = chart.getContext("2d");
    this.gyroChart = new Chart(ctx, {
      type: 'bar',
      data: this.gyroChartData,
      options: {
        scales: {
          yAxes: [{
            ticks: {
              suggestedMin: -360,
              suggestedMax: 360
            }
          }]
        },
        legend: { display: false },
        tooltips: { enabled: false },
        hover: { mode: null }
      }
    });
  }

  chartAccelUpdate() {
    this.accelChart.data.datasets[0].data[0] = this.bmi088_accel.accel_x;
    this.accelChart.data.datasets[0].data[1] = this.bmi088_accel.accel_y;
    this.accelChart.data.datasets[0].data[2] = this.bmi088_accel.accel_z;
    this.accelChart.update();
  }

  chartGyroUpdate() {
    this.gyroChart.data.datasets[0].data[0] = this.bmi088_gyro.anglvel_x;
    this.gyroChart.data.datasets[0].data[1] = this.bmi088_gyro.anglvel_y;
    this.gyroChart.data.datasets[0].data[2] = this.bmi088_gyro.anglvel_z;
    this.gyroChart.update();
  }

  getString(obj: any) {
    return JSON.stringify(obj);
  }
  getSensorData() {
    this.backend.getSensorData<BME680[]>("bme680")
      .subscribe(
        data => {
          this.bme = data
          //console.log(this.bme)
        }
      )

    this.backend.getSensorData<any>("ams")
      .subscribe(
        (data: AMS[]) => {
          this.ams = data
          //console.log(JSON.stringify(this.ams))
        }
      )

    this.backend.getSensorData<BMI088_ACCEL>("bmi088_accel")
      .subscribe(
        data => {
          this.bmi088_accel = data
          //console.log(this.bmi_accel)
        }
      )

    this.backend.getSensorData<BMI088_GYRO>("bmi088_gyro")
      .subscribe(
        data => {
          this.bmi088_gyro = data
          //console.log(this.bmi088_gyro)
        }
      )
  }

  onGyroChange(event: MatSliderChange) {
    this.motorSpeed_gyro = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorspeed_1", this.motorSpeed_gyro).subscribe()
  }

  onAccelChange(event: MatSliderChange) {
    this.motorSpeed_accel = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorspeed_1", this.motorSpeed_accel).subscribe()
  }


}

