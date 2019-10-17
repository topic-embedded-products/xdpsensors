import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { RequestOptions, Request, Headers } from '@angular/http';

@Injectable({
  providedIn: 'root'
})
export class BackendService {

  constructor(private http: HttpClient) { }
  /**
  * Function to extract the data when the server return some
  *
  * @param res
  */
  private extractData(res: Response) {
    let body = res;
    return body || [];
  }

  /**
  * Handle Http operation that failed.
  * Let the app continue.
  * @param operation - name of the operation that failed
  * @param result - optional value to return as the observable result
  */
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(error); // log to console instead
      return of(result as T);
    };
  }

  getSensorData<T>(api: string): Observable<T> {
    let requestAddr = api;
    //console.log(requestAddr)
    return this.http.get<T>(requestAddr)
      .pipe(
        //tap(_ => console.log('fetched data'))
        //  map(this.extractData)
      );
  }

  /** POST: send motor speed in % */
  sendMotorSpeed(api: string, motorType: string, speed: number): Observable<number> {
    //console.log(api + "?" + motorType + "=" + speed)
    return this.http.get<number>(api + "?" + motorType + "=" + speed)
      .pipe(
        catchError(this.handleError('sendMotorSpeed', speed))
      );
  }
  /** POST: send input settings for cameras*/
  sendCamSettings(api: string, cam_sel: string, filter1: string, filter2: string): Observable<number> {
    console.log(api + "?cam_sel=" + cam_sel + "&filter_1="+filter1 + "&filter_2="+filter2)
    return this.http.get<number>(api + "?cam_sel=" + cam_sel + "&filter_1="+filter1 + "&filter_2="+filter2)
      .pipe(
        catchError(this.handleError('set cam settings', 1))
      );
  }

}
export interface BME680 {
  humidityrelative: number;
  pressure: number;
  resistance: number;
  temp: number;
}

export class AMS {
  remote_temp: number;
  pl_temp: number;
  ps_temp: number;
}

export interface BMI088_GYRO {
  anglvel_y: number;
  anglvel_x: number;
  anglvel_z: number;
  temp: number;
}

export interface BMI088_ACCEL {
  accel_z: number;
  accel_x: number;
  accel_y: number;
  temp: number;
}
export interface BMM150_MAGN {
  magn_z: number;
  magn_x: number;
  magn_y: number;
}

export interface Data_Througput {
  Raptor: number;
  XDP   : number;
  Time  : number;
}