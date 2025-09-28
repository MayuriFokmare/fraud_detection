import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FraudDetection {
  private baseUrl = environment.apiUrl;
  private predictUrl = `${this.baseUrl}/predict-upload`;

  constructor(private http: HttpClient) {}

  // Run detection after upload
  runDetection(): Observable<any> {
    return this.http.get(`${this.baseUrl}/runs/`);
  }

  // Fetch fake reviews table
  getFakeReviews(): Observable<any> {
    return this.http.get(`${this.baseUrl}/fake-reviews/`);
  }

  // Close analytics
  closeAnalytics(): Observable<any> {
    return this.http.post(`${this.baseUrl}/close/`, {});
  }

  // Fetch metrics
  getMetrics(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/fraud-detection/metrics/`);
  }

  // Fraud vs Legit analytics
  getFraudVsLegit(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/analytics/fraud-vs-legit/`);
  }

  // Hourly transactions
  getHourlyTransactions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/analytics/hourly-transactions/`);
  }

  // Predict upload (with fraud type + file + username)
  predictUpload(fraudType: string, file: File, username: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', username);

    return this.http.post(`${this.predictUrl}/${fraudType}/`, formData);
  }

  // Fetch summary
  getSummary(): Observable<any> {
    return this.http.get(`${this.baseUrl}/temp-summary/`);
  }

  // Clear temp table
  clearTemp(): Observable<any> {
    return this.http.post(`${this.baseUrl}/clear-temp/`, {});
  }

  // Upload file + fraud type + merchant name
  uploadFile(fraudType: string, merchantName: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('fraud_type', fraudType);
    formData.append('merchant_name', merchantName);
    formData.append('file', file);

    return this.http.post(`${this.baseUrl}/predict-upload/`, formData);
  }

  // Category summary
  getCategorySummary(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/temp-category/`);
  }

  // Merchant fraud summary
  getMerchantFraudSummary(merchant: string): Observable<any> {
    return this.http.get<any>(
      `${this.baseUrl}/merchant-fraud-summary/?merchant=${merchant}`
    );
  }
}