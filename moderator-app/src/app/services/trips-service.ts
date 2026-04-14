import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { BehaviorSubject, map, Observable } from 'rxjs';
import { Trip } from '../components/trips/trips';

@Injectable({
  providedIn: 'root',
})
export class TripsService {
  public eventSource: EventSource | null = null;
  private tripEventSubject = new BehaviorSubject<{ event: string, tripId: string } | null>(null);
  public tripEvents$ = this.tripEventSubject.asObservable();
  constructor(private httpClient: HttpClient) {}

  getTrips(): Observable<Trip[]> {
    return this.httpClient
      .get<{ trips: Trip[] }>(`${environment.apiUrl}/trips`)
      .pipe(map((response) => response.trips));
  }

  getTrip(tripId: string): Observable<Trip> {
    return this.httpClient.get<Trip>(`${environment.apiUrl}/trips/${tripId}`);
  }

  claimTrip(tripId: string): Observable<{ success: boolean }> {
    return this.httpClient.patch<{ success: boolean; trip: Trip }>(
      `${environment.apiUrl}/trips/${tripId}/claim`,
      {},
    );
  }

  acknowledgeTrip(tripId: string): Observable<{ success: boolean }> {
    return this.httpClient.patch<{ success: boolean }>(
      `${environment.apiUrl}/trips/${tripId}/acknowledge`,
      {},
    );
  }

  connectEventSource(): void {
    this.eventSource = new EventSource(`${environment.apiUrl}/events`, { withCredentials: true });
    this.eventSource.onmessage = (event) => {
      const tripEvent = JSON.parse(event.data);
      this.emitTripEvent(tripEvent);
    };
  }

  closeEventSource(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  emitTripEvent(event: { event: string, tripId: string }) {
    this.tripEventSubject.next(event);
  }
}
