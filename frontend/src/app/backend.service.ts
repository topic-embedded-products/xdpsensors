import {Injectable} from '@angular/core';
import {Http, Response} from '@angular/http';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {Observable, of} from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class BackendService {

  private localServer = "http://localhost:8080/"
  //private controller = "bme680"
  
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
  private handleError<T> (operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(error); // log to console instead
      return of(result as T);
    };
  }

  getSensorData<T>(api: string): Observable<T> {
    return this.http.get<T>(this.localServer+api)
    .pipe(
      //tap(_ => console.log('fetched data'))
    //  map(this.extractData)
    );
  }

  /** POST: send motor speed in % */
  sendMotorSpeed (speed: number): Observable<number> {
    return this.http.post<number>(this.localServer, speed)
      .pipe(
        catchError(this.handleError('addHero', speed))
      );
  }

}
export class BME680 {
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

export class BMI088_GYRO {
  anglvel_y: number;
  anglvel_x: number;
  anglvel_z: number;
  temp: number;
}

export class BMI088_ACCEL {
  accel_z: number;
  accel_x: number;
  accel_y: number;
  temp: number;
}