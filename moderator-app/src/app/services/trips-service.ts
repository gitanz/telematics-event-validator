import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { map, Observable } from 'rxjs';
import { Trip } from '../components/trips/trips';

@Injectable({
  providedIn: 'root',
})
export class TripsService {
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
}
