import { BrowserModule, HAMMER_GESTURE_CONFIG } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpModule} from '@angular/http';
import { HttpClientModule } from '@angular/common/http';
import { GestureConfig } from '@angular/material';

import {
  MatCardModule, 
  //MatInputModule,
  MatButtonModule,
  MatFormFieldModule,
  MatInputModule,
  MatRippleModule,
  MatSliderModule
} from '@angular/material';

import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatRippleModule,
    MatSliderModule,
    BrowserModule,
    HttpModule,
    HttpClientModule
  ],
  exports:[
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatRippleModule,
    MatSliderModule
  ],
  providers: [ { provide: HAMMER_GESTURE_CONFIG, useClass: GestureConfig },],
  bootstrap: [AppComponent]
})
export class AppModule { }
