import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FraudDetection {
  private baseUrl = 'http://127.0.0.1:8000/api';
  private predictUrl = 'http://127.0.0.1:8000/api/predict-upload';

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

  getMetrics() {
  return this.http.get<any[]>('http://127.0.0.1:8000/api/fraud-detection/metrics/');
}

// fraud-detection.service.ts
getFraudVsLegit(): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/analytics/fraud-vs-legit/`);
}

getHourlyTransactions(): Observable<any[]> {
  return this.http.get<any[]>(`${this.baseUrl}/analytics/hourly-transactions/`);
}

predictUpload(fraudType: string, file: File, username: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', username); // backend can use this

    return this.http.post(`${this.predictUrl}/${fraudType}/`, formData);
  }

  //  Fetch summary
  getSummary(): Observable<any> {
    return this.http.get(`${this.baseUrl}/temp-summary/`);
  }

  //  Clear temp table
  clearTemp(): Observable<any> {
    return this.http.post(`${this.baseUrl}/clear-temp/`, {});
  }

  //  Upload file + fraud type + merchant name
uploadFile(fraudType: string, merchantName: string, file: File): Observable<any> {
  const formData = new FormData();
  formData.append('fraud_type', fraudType);
  formData.append('merchant_name', merchantName);
  formData.append('file', file);

  return this.http.post(`${this.baseUrl}/predict-upload/`, formData);
}

getCategorySummary() {
  return this.http.get<any[]>('http://127.0.0.1:8000/api/temp-category/');
}

getMerchantFraudSummary(merchant: string) {
  return this.http.get<any>(
    `http://127.0.0.1:8000/api/merchant-fraud-summary/?merchant=${merchant}`
  );
}

}
