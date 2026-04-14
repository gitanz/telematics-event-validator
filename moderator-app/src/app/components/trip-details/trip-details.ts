import { ChangeDetectorRef, Component, Input } from '@angular/core';
import { Trip } from '../trips/trips';
import { TripsService } from '../../services/trips-service';
import { MatDivider, MatList, MatListItem, MatListSubheaderCssMatStyler } from '@angular/material/list';
import { MatButton } from '@angular/material/button';
import { concatMap } from 'rxjs';

@Component({
  selector: 'app-trip-details',
  imports: [MatList, MatListItem, MatButton, MatListSubheaderCssMatStyler, MatDivider],
  templateUrl: './trip-details.html',
  styleUrl: './trip-details.css',
})
export class TripDetails {
  @Input() trip: Trip | undefined;

  constructor(
    private tripService: TripsService,
    private cdr: ChangeDetectorRef
  ) {}

  protected claimTrip(tripId: string) {
    this.tripService
      .claimTrip(tripId)
      .pipe(
        concatMap((success) => this.tripService.getTrip(tripId))
      )
      .subscribe((trip) => {
        this.trip = trip;
        this.cdr.detectChanges();
      });
  }
  protected acknowledgeTrip(tripId: string) {
    this.tripService
      .acknowledgeTrip(tripId)
      .pipe(concatMap((success) => this.tripService.getTrip(tripId)))
      .subscribe((trip) => {
        this.trip = trip;
        this.cdr.detectChanges();
      });
  }
}
