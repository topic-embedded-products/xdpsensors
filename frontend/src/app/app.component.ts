import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { BackendService, BME680, AMS, BMI088_ACCEL, BMI088_GYRO, BMM150_MAGN, Data_Througput } from './backend.service';
import 'rxjs/add/operator/map'
import { Subscription, timer, pipe, from, interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { MatSliderChange, MatRadioButton } from '@angular/material'
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

  private data_url: string = "";
  public video_loc: string = this.data_url+"video";
  title = 'drone-frontend';
  private sensorData: Observable<any>
  bme: BME680;
  private ams: AMS[];
  private bmi088_accel: BMI088_ACCEL;
  private bmi088_gyro: BMI088_GYRO;
  bmm150_magn: BMM150_MAGN;
  data_thr: Data_Througput;

  bme680_subscription: Subscription;
  ams_subscription: Subscription;
  bmi088_accel_subscription: Subscription;
  bmi088_gyro_subscription: Subscription;
  bmm150_magn_subscription: Subscription;
  motorspeed1_subscription: Subscription;
  motorspeed2_subscription: Subscription;
  motorspeed3_subscription: Subscription;
  motorspeed4_subscription: Subscription;
  data_thr_subscription: Subscription;
  frame_poll: Subscription;
  frame_interval = 1000; //ms
  subInterval = 1000; //ms

  motorSpeed_1 = 0;
  motorSpeed_2 = 0;
  motorSpeed_3 = 0;
  motorSpeed_4 = 0;
  data_throughput = 0;
  imagepath = "assets/img/com_ts.png"
  dyplo_img_path = "assets/img/Dyplo-logo.png"
  temp_video_path = "assets/img/camera.jpg"
  arrow_right_img_path = "assets/img/arrow_right_sc.png"
  arrow_up_img_path = "assets/img/arrow_up.png"
  state: string = 'default';

  mode1_val: string = "none";
  mode2_val: string = "none";
  cam_val: string = "cam_1";

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

  constructor(private backend: BackendService, private animationBuilder: AnimationBuilder, private elRef: ElementRef) {
    this.accelChartData = {};
    this.gyroChartData = {};

    this.bme = {
      humidityrelative: 0,
      pressure: 0,
      resistance: 0,
      temp: 0
    };

    this.bmi088_accel = {
      accel_x: 0,
      accel_y: 0,
      accel_z: 0,
      temp: 0
    };

    this.bmi088_gyro = {
      anglvel_x: 0,
      anglvel_y: 0,
      anglvel_z: 0,
      temp: 0
    };

    this.bmm150_magn = {
      magn_x: 0,
      magn_y: 0,
      magn_z: 0
    };
  }

  ngOnInit(): void {
    this.rotationAngle = 0;
    // get motor speed data (use negative number to get data)
    this.motorspeed1_subscription = timer(0, this.subInterval)
    .pipe(
      switchMap(() => this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_1", -1)))
    .subscribe(result => {
      this.motorSpeed_1 = result;
    });

    this.motorspeed2_subscription = timer(0, this.subInterval)
    .pipe(
      switchMap(() => this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_2", -1)))
    .subscribe(result => {
      this.motorSpeed_2 = result;
    });

    this.motorspeed3_subscription = timer(0, this.subInterval)
    .pipe(
      switchMap(() => this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_3", -1)))
    .subscribe(result => {
      this.motorSpeed_3 = result;
    });

    this.motorspeed4_subscription = timer(0, this.subInterval)
    .pipe(
      switchMap(() => this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_4", -1)))
    .subscribe(result => {
      this.motorSpeed_4 = result;
    });

    this.frame_poll = timer(0, this.frame_interval).subscribe(val => {this.setLinkPicture(this.video_loc);});

    this.bmm150_magn_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BMM150_MAGN>(this.data_url+"bmm150_magn")))
      .subscribe(result => {
        this.bmm150_magn = result;
        // if (typeof this.bmm150_magn.resistance === "string") {
        let heading = Math.atan2(this.bmm150_magn.magn_y, this.bmm150_magn.magn_x);
        if(heading < 0)
          heading += 2*Math.PI;
        if(heading > 2*Math.PI)
          heading -= 2*Math.PI;
        this.rotationAngle = Math.round(heading * 180/Math.PI);
        // }
        // else {
        //   this.rotationAngle = this.bme.resistance;
        // }
        this.rotateCompass();
      });

    this.bme680_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BME680>(this.data_url+"bme680")))
      .subscribe(result => {
        this.bme = result;
      });

    this.ams_subscription = timer(0, this.subInterval).pipe(
      switchMap(() => this.backend.getSensorData<AMS[]>(this.data_url+"ams"))
    ).subscribe(result => this.ams = result);

    this.bmi088_accel_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BMI088_ACCEL>(this.data_url+"bmi088_accel")))
      .subscribe(result => {
        this.bmi088_accel = result;
        this.chartAccelUpdate();
      });

    this.bmi088_gyro_subscription = timer(0, this.subInterval)
      .pipe(
        switchMap(() => this.backend.getSensorData<BMI088_GYRO>(this.data_url+"bmi088_gyro")))
      .subscribe(result => {
        this.bmi088_gyro = result;
        this.chartGyroUpdate();
      });

    this.data_thr_subscription = timer(0, this.subInterval)
        .pipe(
          switchMap(() => this.backend.getSensorData<Data_Througput>(this.data_url+"throughput")))
        .subscribe(result => {
            this.data_thr = result;
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
      labels: ["Roll", "Pitch", "Yaw"],
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
    this.motorspeed1_subscription.unsubscribe();
    this.motorspeed2_subscription.unsubscribe();
    this.motorspeed3_subscription.unsubscribe();
    this.motorspeed4_subscription.unsubscribe();
    this.data_thr_subscription.unsubscribe();
    this.frame_poll.unsubscribe();
  }

  public ngAfterViewInit() {
    let chart = this.refAccelChart.nativeElement;
    let ctx = chart.getContext("2d");
    this.accelChart = new Chart(chart, {
      type: 'bar',
      data: this.accelChartData,
      options: {
        scales: {
          yAxes: [{
            ticks: {
              fontColor: "white",
              suggestedMin: -1,
              suggestedMax: 1
            }
          }],
          xAxes: [{
            ticks: {
              fontColor: "white"
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
              fontColor: "white",
              suggestedMin: -1,
              suggestedMax: 1
            }
          }],
          xAxes: [{
            ticks: {
              fontColor: "white"
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
    this.backend.getSensorData<BME680>(this.data_url+"bme680")
      .subscribe(
        data => {
          this.bme = data
        }
      )

    this.backend.getSensorData<any>(this.data_url+"ams")
      .subscribe(
        (data: AMS[]) => {
          this.ams = data
        }
      )

    this.backend.getSensorData<BMI088_ACCEL>(this.data_url+"bmi088_accel")
      .subscribe(
        data => {
          this.bmi088_accel = data
        }
      )

    this.backend.getSensorData<BMI088_GYRO>(this.data_url+"bmi088_gyro")
      .subscribe(
        data => {
          this.bmi088_gyro = data
        }
      )
    this.backend.getSensorData<BMM150_MAGN>(this.data_url+"bmm150_magn")
      .subscribe(
        data => {
          this.bmm150_magn = data
        }
      )
    this.backend.getSensorData<Data_Througput>(this.data_url+"throughput")
      .subscribe(
        data => {
          console.log(data);
          this.data_thr = data
        }
      )
  }

  onMotor1Change(event: MatSliderChange) {
    this.motorSpeed_1 = event.value;
    this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_1", this.motorSpeed_1).subscribe(data => {this.motorSpeed_1 = data})
  }

  onMotor2Change(event: MatSliderChange) {
    this.motorSpeed_2 = event.value;
    this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_2", this.motorSpeed_2).subscribe(data => {this.motorSpeed_2 = data})
  }

  onMotor3Change(event: MatSliderChange) {
    this.motorSpeed_3 = event.value;
    this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_3", this.motorSpeed_3).subscribe(data => {this.motorSpeed_3 = data})
  }

  onMotor4Change(event: MatSliderChange) {
    this.motorSpeed_4 = event.value;
    this.backend.sendMotorSpeed(this.data_url+"motorspeed", "motorSpeed_4", this.motorSpeed_4).subscribe(data => {this.motorSpeed_4 = data})
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

  sendCamSettings(){
    this.backend.sendCamSettings(this.data_url+"cam_control", this.cam_val, this.mode1_val, this.mode2_val).subscribe()
  }

  linkPicture: string;
  timeStamp : number;
  getLinkPicture() {
    if(this.timeStamp) {
       return this.linkPicture + '?' + this.timeStamp;
    }
    return this.linkPicture;
  }

  setLinkPicture(url: string) {
    this.linkPicture = url;
    this.timeStamp = (new Date()).getTime();
  }

}
