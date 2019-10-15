import { BrowserModule, HAMMER_GESTURE_CONFIG } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpModule} from '@angular/http';
import { HttpClientModule } from '@angular/common/http';
import { GestureConfig } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {FormsModule} from '@angular/forms';

import {
  MatCardModule, 
  //MatInputModule,
  MatButtonModule,
  MatOptionModule,
  MatSelectModule,
  MatRadioModule,
  MatFormFieldModule,
  MatInputModule,
  MatRippleModule,
  MatGridListModule,
  MatSliderModule
} from '@angular/material';

import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserAnimationsModule,
    MatCardModule,
    MatGridListModule,
    MatButtonModule,
    MatSelectModule,
    MatOptionModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatRippleModule,
    MatSliderModule,
    BrowserModule,
    HttpModule,
    FormsModule,
    HttpClientModule
  ],
  exports:[
    MatCardModule,
    MatGridListModule,
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
