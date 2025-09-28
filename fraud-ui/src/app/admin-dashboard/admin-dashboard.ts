import { Component, OnInit, ChangeDetectorRef, ViewChildren, QueryList, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Chart } from 'chart.js/auto';

// PrimeNG
import { TableModule } from 'primeng/table';
import { PaginatorModule } from 'primeng/paginator';
import { ButtonModule } from 'primeng/button';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    TableModule,
    PaginatorModule,
    ButtonModule
  ],
  templateUrl: './admin-dashboard.html',
  styleUrls: ['./admin-dashboard.css']
})
export class AdminDashboard implements OnInit {
  fraudSummary: any[] = [];
  merchantFraud: any[] = [];
  fraudulentRecords: any[] = [];
  filteredRecords: any[] = [];

  fraudCharts: Chart[] = [];
  merchantChart: Chart | null = null;

  selectedFraudType: string = '';
  rows = 10;

  private baseUrl = environment.apiUrl;   // ✅ dynamic API base URL

  @ViewChildren('fraudCanvas') fraudCanvasList!: QueryList<ElementRef<HTMLCanvasElement>>;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadFraudSummary();
    this.loadMerchantFraud();
    this.loadFraudulentRecords();
  }

  loadFraudSummary() {
    this.http.get<any[]>(`${this.baseUrl}/admin-dashboard/fraud-summary/`)
      .subscribe(res => {
        this.fraudSummary = res;
        this.cdr.detectChanges();
        this.renderFraudCharts();
      });
  }

  loadMerchantFraud() {
    this.http.get<any[]>(`${this.baseUrl}/admin-dashboard/merchant-fraud/`)
      .subscribe(res => {
        this.merchantFraud = res;
        this.cdr.detectChanges();
        this.renderMerchantChart();
      });
  }

  loadFraudulentRecords() {
    this.http.get<any[]>(`${this.baseUrl}/admin-dashboard/fraudulent-records/`)
      .subscribe(res => {
        this.fraudulentRecords = res;
        this.filteredRecords = [...this.fraudulentRecords];
      });
  }

  applyFilter() {
    this.filteredRecords = this.selectedFraudType
      ? this.fraudulentRecords.filter(r => r.fraud_type === this.selectedFraudType)
      : [...this.fraudulentRecords];
  }

  exportCSV() {
    const header = ['Transaction ID', 'Merchant', 'Fraud Type', 'Text', 'Status'];
    const rows = this.filteredRecords.map(r => [
      r.transaction_id,
      r.merchant_name,
      r.fraud_type,
      r.captured_text,
      r.status ? 'FRAUD' : 'REAL'
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,'
      + header.join(',') + '\n'
      + rows.map(e => e.map(v => `"${v}"`).join(',')).join('\n');

    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', 'fraudulent_records.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  renderFraudCharts() {
    this.fraudCharts.forEach(c => c.destroy());
    this.fraudCharts = [];

    this.fraudCanvasList.forEach((canvasRef, i) => {
      const item = this.fraudSummary[i];
      const ctx = canvasRef.nativeElement;

      const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Fraudulent', 'Non-Fraudulent'],
          datasets: [{
            data: [item.fraudulent, item.non_fraudulent],
            backgroundColor: ['#e74c3c', '#2ecc71']
          }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
      });
      this.fraudCharts.push(chart);
    });
  }

  renderMerchantChart() {
    if (this.merchantChart) this.merchantChart.destroy();

    const ctx = document.getElementById('merchantChart') as HTMLCanvasElement;
    if (ctx) {
      this.merchantChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.merchantFraud.map(m => m.merchant_name),
          datasets: [
            { label: 'Total', data: this.merchantFraud.map(m => m.total), backgroundColor: '#3498db' },
            { label: 'Fraudulent', data: this.merchantFraud.map(m => m.fraudulent), backgroundColor: '#e74c3c' }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } }
        }
      });
    }
  }
}