import { ChangeDetectorRef, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Trip } from '../trips/trips';
import { TripsService } from '../../services/trips-service';
import { MatDivider, MatList, MatListItem, MatListSubheaderCssMatStyler } from '@angular/material/list';
import { MatButton } from '@angular/material/button';
import { concatMap, Subject, takeUntil } from 'rxjs';
import { HomePageService } from '../../services/home-page-service';

@Component({
  selector: 'app-trip-details',
  imports: [MatList, MatListItem, MatButton, MatListSubheaderCssMatStyler, MatDivider],
  templateUrl: './trip-details.html',
  styleUrl: './trip-details.css',
})
export class TripDetails implements OnInit, OnDestroy {
  @Input() trip: Trip | undefined;

  private destroy$ = new Subject<void>();

  constructor(
    private homePageService: HomePageService,
    private tripService: TripsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.tripService.tripEvents$
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (event) => {
          if (!event) {
            return;
          }

          if(event.tripId === this.trip?.tripId) {
            this.homePageService.clearSelectedTrip();
          }

          this.cdr.detectChanges();
        },
      });
  }

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
      .subscribe((success) => {
        this.homePageService.clearSelectedTrip();
        this.tripService.emitTripEvent({ event: 'acknowledge', tripId });
        this.cdr.detectChanges();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  protected closeDetails() {
    this.homePageService.clearSelectedTrip()
  }
}
