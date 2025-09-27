import { Component, OnInit, OnDestroy, ViewChild, ElementRef, NgZone, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import Chart from 'chart.js/auto';
import { FraudDetection } from '../fraud-detection';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { of, Subject, fromEvent } from 'rxjs';
import { catchError, debounceTime, finalize, switchMap, takeUntil, tap } from 'rxjs/operators';

export type FraudType = 'fake_review' | 'payment' | 'chargeback' | 'merchant';

export interface Transaction {
  transaction_id: string | number;
  captured_text: string;
  status: 'Fraud' | 'Non-Fraud' | string;
  [key: string]: any;
}

export interface Summary {
  fraud_type: FraudType;
  total_transactions: number;
  total_fraud: number;
  total_non_fraud: number;
  fraud_percentage: number;
  transactions: Transaction[];
}

export interface CategoryBucket {
  captured_text: string;
  fraud: number;
  non_fraud: number;
}

export interface FraudSummaryRow {
  fraud_type: string;
  total_transactions: number;
  fraudulent: number;
  non_fraudulent: number;
  fraud_percentage: number;
}

export interface MerchantFraudSummary {
  merchant_name: string;
  fraud_summary: FraudSummaryRow[];
  totalTransactions?: number;
  totalFraudTransactions?: number;
  totalNonFraudTransaction?: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, TableModule, TagModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class Dashboard implements OnInit, OnDestroy {
  username = '';
  fraudType: FraudType | '' = '';
  fraudTypes: FraudType[] = ['fake_review', 'payment', 'chargeback', 'merchant'];
  file: File | null = null;

  summary: Summary | null = null;
  transactions: Transaction[] = [];
  merchantSummary: MerchantFraudSummary | null = null;
  loading = false;

  private donutChart: Chart | null = null;            // post-detection donut
  private merchantDonutChart: Chart | null = null;    // pre-detection donut
  private barChart: Chart | null = null;
  private destroy$ = new Subject<void>();

  @ViewChild('donutCanvas') donutCanvas?: ElementRef<HTMLCanvasElement>;
  @ViewChild('barCanvas') barCanvas?: ElementRef<HTMLCanvasElement>;

  private zone = inject(NgZone);

  constructor(private fraudService: FraudDetection) {}

  ngOnInit(): void {
    this.username = localStorage.getItem('username') || 'Unknown User';

    // Load merchant summary on page load (example merchant; replace if needed)
    this.fraudService.getMerchantFraudSummary('Retail')
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (res) => {
          this.merchantSummary = res;
          this.renderMerchantDonut(); // draw pre-detection donut
        },
        error: (err) => console.error('Error fetching merchant summary', err)
      });

    // Handle chart resize
    this.zone.runOutsideAngular(() => {
      fromEvent(window, 'resize')
        .pipe(debounceTime(150), takeUntil(this.destroy$))
        .subscribe(() => {
          this.donutChart?.resize();
          this.merchantDonutChart?.resize();
          this.barChart?.resize();
        });
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.donutChart?.destroy();
    this.merchantDonutChart?.destroy();
    this.barChart?.destroy();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    if (!file) { this.file = null; return; }

    const maxSizeMB = 25;
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`File too large. Max ${maxSizeMB}MB.`);
      input.value = '';
      this.file = null;
      return;
    }
    this.file = file;
  }

  runDetection() {
    if (!this.fraudType || !this.file) {
      alert('Please select fraud type and choose a file.');
      return;
    }

    this.loading = true;

    of(null)
      .pipe(
        switchMap(() => this.fraudService.uploadFile(this.fraudType, this.username, this.file!)),
        switchMap(() => this.fraudService.getSummary()),
        tap((res: Summary) => {
          // Hide pre-detection donut safely
          if (this.merchantDonutChart) { this.merchantDonutChart.destroy(); this.merchantDonutChart = null; }

          this.summary = res;
          this.transactions = res.transactions || [];
          queueMicrotask(() => this.renderPostDetectionDonut());
        }),
        switchMap((res: Summary) => {
          const needsCategory = res.fraud_type === 'merchant' || res.fraud_type === 'payment';
          return needsCategory ? this.fraudService.getCategorySummary() : of(null);
        }),
        tap((catRes: CategoryBucket[] | null) => {
          if (catRes) this.renderBar(catRes);
          else { this.barChart?.destroy(); this.barChart = null; }
        }),
        finalize(() => (this.loading = false)),
        catchError((err) => {
          console.error('Detection failed', err);
          this.loading = false;
          alert('Detection failed. Please try again.');
          return of(null);
        }),
        takeUntil(this.destroy$)
      )
      .subscribe();
  }

  /** ===== Pre-detection merchant donut: Fraud vs Legit ===== */
  private renderMerchantDonut() {
    if (!this.merchantSummary) return;

    if (this.merchantDonutChart) { this.merchantDonutChart.destroy(); this.merchantDonutChart = null; }

    setTimeout(() => {
      const ctx = document.getElementById('merchantDonutChart') as HTMLCanvasElement;
      if (ctx) {
        this.merchantDonutChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Fraud', 'Legit'],
            datasets: [
              {
                data: [
                  this.merchantSummary!.totalFraudTransactions ?? 0,
                  this.merchantSummary!.totalNonFraudTransaction ?? 0
                ],
                backgroundColor: ['#e74c3c', '#2ecc71']
              }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false }
        });
      }
    }, 0);
  }

  /** ===== Post-detection donut (your existing one) ===== */
  private renderPostDetectionDonut() {
    if (!this.summary) return;

    if (this.donutChart) { this.donutChart.destroy(); this.donutChart = null; }

    setTimeout(() => {
      const ctx1 = document.getElementById('donutChart') as HTMLCanvasElement;
      if (ctx1) {
        this.donutChart = new Chart(ctx1, {
          type: 'doughnut',
          data: {
            labels: ['Fraud', 'Non-Fraud'],
            datasets: [
              {
                data: [this.summary!.total_fraud, this.summary!.total_non_fraud],
                backgroundColor: ['#e74c3c', '#2ecc71']
              }
            ]
          },
          options: { responsive: true, maintainAspectRatio: false }
        });
      }
    }, 0);
  }

  private renderBar(categoryData: CategoryBucket[]) {
    if (!this.summary) return;

    if (this.barChart) { this.barChart.destroy(); this.barChart = null; }

    const labels = categoryData.map((item) => item.captured_text);
    const fraudCounts = categoryData.map((item) => item.fraud);
    const nonFraudCounts = categoryData.map((item) => item.non_fraud);

    setTimeout(() => {
      const ctx2 = document.getElementById('barChart') as HTMLCanvasElement;
      if (ctx2) {
        this.barChart = new Chart(ctx2, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              { label: 'Fraud', data: fraudCounts, backgroundColor: '#e74c3c', barThickness: 20 },
              { label: 'Non-Fraud', data: nonFraudCounts, backgroundColor: '#2ecc71', barThickness: 20 }
            ]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
              x: { stacked: true, beginAtZero: true },
              y: { stacked: true, ticks: { autoSkip: false, font: { size: 12 } } }
            }
          }
        });
      }
    }, 0);
  }

  // --- Export CSV ---
  exportCSV() {
    if (!this.transactions?.length) return;
    const csv = [Object.keys(this.transactions[0]), ...this.transactions.map(o => Object.values(o))]
      .map(r => r.join(",")).join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = `${this.summary?.fraud_type}_transactions.csv`;
    a.click();
  }

  // --- Close Dashboard ---
  closeDashboard() {
    this.fraudService.clearTemp().subscribe({
      next: () => {
        this.summary = null;
        this.transactions = [];
        this.donutChart?.destroy(); this.donutChart = null;
        this.barChart?.destroy(); this.barChart = null;

        // Re-render pre-detection donut if we have merchantSummary
        if (this.merchantSummary) this.renderMerchantDonut();

      },
      error: (err) => {
        console.error('Error clearing temp data', err);
        alert('Failed to clear dashboard.');
      }
    });
  }
}