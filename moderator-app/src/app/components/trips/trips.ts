import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell,
  MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow,
  MatRowDef,
  MatTable,
} from '@angular/material/table';
import { CdkFixedSizeVirtualScroll, CdkVirtualScrollViewport } from '@angular/cdk/scrolling';
import { Subject, takeUntil } from 'rxjs';
import { TripsService } from '../../services/trips-service';
import { HomePageService } from '../../services/home-page-service';
import { AsyncPipe } from '@angular/common';

export interface Location {
  location: string;
  timestamp: string;
}

export interface Trip {
  tripId: string;
  location: string;
  startLocation: string;
  startTimestamp: string;
  endLocation: string;
  endTimestamp: string;
  stops ?: Location[];
  claimedBy ?: string;
  claimedAt ?: string;
  acknowledgedBy ?: string;
  acknowledgedAt ?: string;
}

@Component({
  selector: 'app-trips',
  imports: [
    MatTable,
    MatColumnDef,
    MatHeaderCell,
    MatCell,
    MatCellDef,
    MatHeaderCellDef,
    MatHeaderRow,
    MatRow,
    MatHeaderRowDef,
    MatRowDef,
    CdkVirtualScrollViewport,
    CdkFixedSizeVirtualScroll,
    AsyncPipe,
  ],
  templateUrl: './trips.html',
  styleUrl: './trips.css',
})
export class Trips implements OnInit, OnDestroy {
  displayedColumns: string[] = [
    'tripId',
    'location',
    'startLocation',
    'startTimestamp',
    'endLocation',
    'endTimestamp',
  ];
  dataSource: Trip[] = [];
  trackBy = (index: number, el: Trip) => el.tripId;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private tripService: TripsService,
    protected homePageService: HomePageService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.tripService
      .getTrips()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (trips) => {
          this.dataSource = trips;
        },
      });

    this.tripService.connectEventSource();
    this.tripService.tripEvents$.pipe(takeUntil(this.destroy$)).subscribe({
      next: (event) => {
        if (!event) {
          return;
        }
        this.dataSource = this.dataSource.filter((trip) => trip.tripId !== event.tripId);
        this.cdr.detectChanges();
        console.log('removing trip with id', event.tripId);
      },
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.tripService.closeEventSource();
  }

  protected viewTrip(tripId: string) {
    this.tripService.getTrip(tripId).subscribe({
      next: (trip: Trip) => {
        this.homePageService.setSelectedTrip(trip);
      },
      error: (err) => console.error('Failed to load trip details:', err),
    });
  }
}
