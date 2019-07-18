import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { BackendService, BME680, AMS, BMI088_ACCEL, BMI088_GYRO } from './backend.service';
import 'rxjs/add/operator/map'
import { Subscription, timer, pipe, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { MatSliderChange } from '@angular/material'
import { Chart } from 'chart.js';
import { trigger, state, style, animate, transition } from '@angular/animations';
import { AnimationBuilder } from '@angular/animations';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  animations: [
    // Each unique animation requires its own trigger. The first argument of the trigger function is the name
    trigger('rotatedState', [
      state('*', style({ transform: 'rotate({{ degparam }}deg)' }), { params: { degparam: 180 } }),
      transition('* => *', animate('250ms ease-in')),
    ])
  ]
})


export class AppComponent implements OnInit {

  title = 'drone-frontend';
  private sensorData: Observable<any>
  bme: BME680;
  private ams: AMS[];
  private bmi088_accel: BMI088_ACCEL;
  private bmi088_gyro: BMI088_GYRO;

  bme680_subscription: Subscription;
  ams_subscription: Subscription;
  bmi088_accel_subscription: Subscription;
  bmi088_gyro_subscription: Subscription;
  subInterval = 1000; //ms

  motorSpeed_1 = 50;
  motorSpeed_2 = 50;
  motorSpeed_3 = 50;
  motorSpeed_4 = 50;

  imagepath = "assets/img/com_ts.png"
  arrowPath = "assets/img/red_arrow.png"
  state: string = 'default';

  @ViewChild("accelChart", { static: false })
  public refAccelChart: ElementRef;
  public accelChartData: any = {};
  private accelChart: Chart;

  @ViewChild("gyroChart", { static: false })
  public refGyroChart: ElementRef;
  public gyroChartData: any = {};
  private gyroChart: Chart;

  @ViewChild("imageContainer", { static: false }) imageContainerElement: ElementRef;
  rotationAngle: number;

  constructor(private backend: BackendService, private animationBuilder: AnimationBuilder) {
    this.accelChartData = {};
    this.gyroChartData = {};
  }

  ngOnInit(): void {
    this.rotationAngle = 0;
    this.bme680_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BME680>("bme680")))
      .subscribe(result => {
        this.bme = result;
        this.rotationAngle = this.bme.resistance;
        this.rotateCompass();
      });

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

    // this.bme.humidityrelative = 0;
    // this.bme.pressure = 0;
    // this.bme.resistance = 0;
    // this.bme.temp = 0;

    let chart = this.refAccelChart.nativeElement;
    let ctx = chart.getContext("2d");
    this.accelChart = new Chart(chart, {
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
              suggestedMin: -1,
              suggestedMax: 1
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
    this.backend.getSensorData<BME680>("bme680")
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

  onMotor1Change(event: MatSliderChange) {
    this.motorSpeed_1 = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorSpeed_1", this.motorSpeed_1).subscribe()
  }

  onMotor2Change(event: MatSliderChange) {
    this.motorSpeed_2 = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorSpeed_2", this.motorSpeed_2).subscribe()
  }

  onMotor3Change(event: MatSliderChange) {
    this.motorSpeed_3 = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorSpeed_3", this.motorSpeed_3).subscribe()
  }

  onMotor4Change(event: MatSliderChange) {
    this.motorSpeed_4 = event.value;
    this.backend.sendMotorSpeed("motorspeed", "motorSpeed_4", this.motorSpeed_4).subscribe()
  }

  rotateCompass() {
    if (!Number.isNaN(this.rotationAngle)) {
      let animationFactory = this.animationBuilder.build([
        style('*'),
        animate('500ms', style({ transform: 'rotate(-' + this.rotationAngle + 'deg)' }))
      ]);
      animationFactory.create(this.imageContainerElement.nativeElement).play();
    }
  }


}

