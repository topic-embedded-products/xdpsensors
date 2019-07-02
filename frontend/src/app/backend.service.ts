import {Injectable} from '@angular/core';
import {Http, Response} from '@angular/http';
import {Observable} from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
 


@Injectable({
  providedIn: 'root'
})
export class BackendService {

  private localServer = "http://localhost:8080/bme680"

  constructor(private http: Http) { }

  getSensorData(): Observable<any> {
    return this.http.get(this.localServer)
  }

}
