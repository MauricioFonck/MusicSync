import { Component, inject, signal } from '@angular/core';
import { MusicSyncApiService, DownloadJob } from '../../core/services/music-sync-api.service';

@Component({
  standalone: true,
  selector: 'app-history',
  template: `<section class="page-heading"><p class="eyebrow">Activity</p><h1>History</h1><p class="muted">Every transfer, in one place.</p></section><div class="panel"><div class="panel-title"><h2>Recent jobs</h2><span class="pill">{{ jobs().length }} jobs</span></div>@if (jobs().length === 0) {<div class="empty"><h3>No syncs yet</h3><p class="muted">Completed transfers will appear here.</p></div>} @else {<div class="history-list">@for (job of jobs(); track job.id) {<article class="history-row"><div><strong>{{ job.source_url }}</strong><p class="muted">{{ job.total_items }} tracks · {{ job.destination_device_id }}</p></div><span class="row-actions"><span class="status" [class.done]="job.status === 'COMPLETED'">{{ job.status }}</span>@if (resumable(job)) {<button class="button subtle" (click)="resume(job)">Resume</button>}@if (cancellable(job)) {<button class="button subtle" (click)="cancel(job)">Cancel</button>}</span></article>}</div>}</div>`,
  styles: [`.panel-title,.history-row{display:flex;justify-content:space-between;align-items:center}.history-list{display:grid}.history-row{padding:1rem 0;border-bottom:1px solid var(--line);gap:1rem}.history-row:last-child{border-bottom:0}.pill,.status{font-size:.75rem;padding:.35rem .65rem;border-radius:99px;background:var(--surface-2);color:var(--muted)}.row-actions{display:flex;gap:.5rem;align-items:center}.status.done{background:#d9f6e9;color:#14734b}`]
})
export class HistoryComponent {
  private readonly api = inject(MusicSyncApiService);
  readonly jobs = signal<DownloadJob[]>([]);
  constructor() { this.load(); }
  load(): void { this.api.history().subscribe({ next: jobs => this.jobs.set(jobs), error: () => this.jobs.set([]) }); }
  resumable(job: DownloadJob): boolean { return ['PAUSED', 'FAILED', 'PARTIALLY_COMPLETED'].includes(job.status); }
  cancellable(job: DownloadJob): boolean { return !['COMPLETED', 'CANCELLED'].includes(job.status); }
  resume(job: DownloadJob): void { this.api.resume(job.id).subscribe({ next: () => this.load() }); }
  cancel(job: DownloadJob): void { this.api.cancel(job.id).subscribe({ next: () => this.load() }); }
}
