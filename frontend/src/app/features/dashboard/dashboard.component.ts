import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, forkJoin, of, switchMap, timer } from 'rxjs';
import { DownloadJob, MusicSyncApiService, StorageDevice } from '../../core/services/music-sync-api.service';

const ACTIVE = ['PENDING', 'ANALYZING', 'DOWNLOADING', 'PROCESSING'];

@Component({
  standalone: true,
  selector: 'app-dashboard',
  imports: [RouterLink],
  template: `
    <section class="page-heading"><p class="eyebrow">Overview</p><h1>Welcome back</h1><p class="muted">Your music workspace at a glance.</p></section>
    <div class="stats-grid">
      <article class="stat-card accent"><span>Current sync</span><strong>{{ currentLabel() }}</strong><small>{{ currentDetail() }}</small></article>
      <article class="stat-card"><span>Tracks synced</span><strong>{{ tracksSynced() }}</strong><small>{{ failedTracks() }} failed · {{ jobs().length }} jobs</small></article>
      <article class="stat-card"><span>Free space</span><strong>{{ freeSpace() }}</strong><small>{{ devices().length ? devices().length + ' device(s) connected' : 'Connect a device to begin' }}</small></article>
    </div>
    <section class="panel welcome"><div><p class="eyebrow">Start a new transfer</p><h2>Bring your collection with you</h2><p class="muted">Analyze a playlist, choose the tracks you want, and MusicSync will prepare them safely for your USB device.</p></div><a class="button primary" routerLink="/downloads">Analyze a source <span>→</span></a></section>
  `,
  styles: [`.welcome { display:flex; justify-content:space-between; align-items:end; gap:2rem; } @media(max-width:700px){.welcome{display:block}.welcome .button{margin-top:1.5rem}}`]
})
export class DashboardComponent {
  private readonly api = inject(MusicSyncApiService);
  readonly jobs = signal<DownloadJob[]>([]);
  readonly devices = signal<StorageDevice[]>([]);

  readonly active = computed(() => this.jobs().filter(job => ACTIVE.includes(job.status)));
  readonly tracksSynced = computed(() => this.jobs().reduce((sum, job) => sum + job.completed_items, 0));
  readonly failedTracks = computed(() => this.jobs().reduce((sum, job) => sum + job.failed_items, 0));
  readonly currentLabel = computed(() => (this.active().length ? `${this.active().length} running` : 'Idle'));
  readonly currentDetail = computed(() => {
    const job = this.active()[0];
    if (job) return `${job.completed_items}/${job.total_items} tracks · ${job.status}`;
    return this.devices().length ? 'USB destination available' : 'No device connected';
  });
  readonly freeSpace = computed(() => {
    const free = this.devices().reduce((sum, device) => sum + device.free_space, 0);
    return this.devices().length ? `${(free / 1_000_000_000).toFixed(1)} GB` : '—';
  });

  constructor() {
    timer(0, 3000)
      .pipe(
        switchMap(() => forkJoin({
          jobs: this.api.history().pipe(catchError(() => of([] as DownloadJob[]))),
          devices: this.api.devices().pipe(catchError(() => of([] as StorageDevice[]))),
        })),
        takeUntilDestroyed(),
      )
      .subscribe(({ jobs, devices }) => { this.jobs.set(jobs); this.devices.set(devices); });
  }
}
