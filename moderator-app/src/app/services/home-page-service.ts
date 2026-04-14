import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Trip } from '../components/trips/trips';

@Injectable({
  providedIn: 'root',
})
export class HomePageService {
  private selectedTripSubject: BehaviorSubject<Trip|null> = new BehaviorSubject<Trip|null>(null);
  public selectedTrip$ = this.selectedTripSubject.asObservable();

  setSelectedTrip(trip: Trip) {
      this.selectedTripSubject.next(trip);
  }

  clearSelectedTrip() {
    this.selectedTripSubject.next(null);
  }
}
