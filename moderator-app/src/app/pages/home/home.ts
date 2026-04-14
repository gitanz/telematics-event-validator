import { Component } from '@angular/core';
import { TripsService } from '../../services/trips-service';
import { Trips } from '../../components/trips/trips';
import { TripDetails } from '../../components/trip-details/trip-details';
import { HomePageService } from '../../services/home-page-service';
import { AsyncPipe } from '@angular/common';


@Component({
  selector: 'app-home',
  templateUrl: './home.html',
  styleUrl: './home.css',
  imports: [Trips, TripDetails, AsyncPipe],
})
export class Home {
  constructor(protected homePageService: HomePageService) {}
}
