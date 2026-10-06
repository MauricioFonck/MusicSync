import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  DownloadJob,
  MusicSyncApiService,
  SearchResult,
  StorageDevice,
} from '../../core/services/music-sync-api.service';

type Source = 'youtube' | 'spotify';
type RowState = DownloadJob | 'starting' | 'error';

const ACTIVE = ['PENDING', 'ANALYZING', 'DOWNLOADING', 'PROCESSING'];

@Component({
  standalone: true,
  selector: 'app-search',
  imports: [FormsModule],
  template: `
    <section class="page-heading">
      <p class="eyebrow">Search</p>
      <h1>Find music</h1>
      <p class="muted">Type a song or artist, pick a result and send it to your USB.</p>
    </section>

    <div class="panel">
      <div class="search-row">
        <input
          [(ngModel)]="query"
          (keyup.enter)="search()"
          placeholder="Artist - Song"
          aria-label="Search query"
        />
        <select [(ngModel)]="source" aria-label="Source">
          <option value="youtube">YouTube</option>
          <option value="spotify">Spotify</option>
        </select>
        <button class="button primary" (click)="search()" [disabled]="loading() || !query.trim()">
          {{ loading() ? 'Searching…' : 'Search' }}
        </button>
      </div>
      @if (source === 'spotify') {
        <p class="muted hint">Spotify returns the best match only and can take about 30 seconds.</p>
      }
      <div class="device-row">
        <label for="device">Send to</label>
        <select id="device" [(ngModel)]="device">
          <option value="" disabled>Select destination</option>
          @for (d of devices(); track d.id) {
            <option [value]="d.id">{{ d.volume_label }} ({{ d.mount_point }})</option>
          }
        </select>
      </div>
      @if (error()) {
        <p class="error">{{ error() }}</p>
      }
    </div>

    @if (searched() && !loading() && results().length === 0 && !error()) {
      <div class="panel"><p class="muted">No results for “{{ lastQuery() }}”.</p></div>
    }

    @if (results().length > 0) {
      <section class="panel">
        <div class="panel-title">
          <h2>Results</h2>
          <span class="pill">{{ results().length }} found</span>
        </div>
        <div class="result-list">
          @for (hit of results(); track hit.url) {
            <article class="result">
              @if (hit.thumbnail_url) {
                <img [src]="hit.thumbnail_url" alt="" loading="lazy" />
              } @else {
                <span class="thumb-fallback">♪</span>
              }
              <div class="result-info">
                <strong>{{ hit.title }}</strong>
                <small>{{ hit.artist }}{{ hit.album ? ' · ' + hit.album : '' }}</small>
              </div>
              <span class="duration">{{ duration(hit.duration_seconds) }}</span>
              <a class="open-link" [href]="hit.url" target="_blank" rel="noopener noreferrer">Open</a>
              <button
                class="button subtle"
                (click)="add(hit)"
                [disabled]="!device || locked(hit.url)"
              >
                {{ label(hit.url) }}
              </button>
              @if (progress(hit.url); as value) {
                <progress max="100" [value]="value"></progress>
              }
            </article>
          }
        </div>
      </section>
    }
  `,
  styles: [
    `
      .search-row { display: flex; gap: 0.75rem; }
      .search-row input { flex: 1; }
      .search-row select, .device-row select { border: 1px solid var(--line); border-radius: 9px; padding: 0.7rem; background: var(--surface); }
      .hint { margin: 0.75rem 0 0; font-size: 0.85rem; }
      .device-row { display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; }
      .panel-title { display: flex; justify-content: space-between; align-items: center; }
      .pill { font-size: 0.75rem; padding: 0.35rem 0.65rem; border-radius: 99px; background: var(--surface-2); color: var(--muted); }
      .result-list { display: grid; margin-top: 1rem; }
      .result { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; padding: 0.8rem 0; border-bottom: 1px solid var(--line); }
      .result:last-child { border-bottom: 0; }
      .result img, .thumb-fallback { width: 4.2rem; height: 2.6rem; border-radius: 8px; object-fit: cover; background: var(--mint); display: grid; place-items: center; font-weight: 800; }
      .result-info { display: grid; gap: 0.2rem; flex: 1; min-width: 12rem; }
      .result-info small, .duration { color: var(--muted); }
      .open-link { color: var(--muted); font-size: 0.85rem; }
      .result progress { width: 100%; }
      .error { color: #b33a36; margin-bottom: 0; }
      @media (max-width: 650px) { .search-row { display: grid; } }
    `,
  ],
})
export class SearchComponent {
  private readonly api = inject(MusicSyncApiService);

  query = '';
  source: Source = 'youtube';
  device = '';
  readonly devices = signal<StorageDevice[]>([]);
  readonly results = signal<SearchResult[]>([]);
  readonly loading = signal(false);
  readonly searched = signal(false);
  readonly error = signal('');
  readonly lastQuery = signal('');
  readonly rows = signal<Record<string, RowState>>({});

  constructor() {
    this.api.devices().subscribe({
      next: devices => {
        this.devices.set(devices);
        this.device ||= devices[0]?.id ?? '';
      },
      error: () => this.devices.set([]),
    });
  }

  search(): void {
    const q = this.query.trim();
    if (!q || this.loading()) return;
    this.loading.set(true);
    this.error.set('');
    this.lastQuery.set(q);
    this.api.search(q, this.source).subscribe({
      next: results => {
        this.results.set(results);
        this.searched.set(true);
        this.loading.set(false);
      },
      error: () => {
        this.results.set([]);
        this.error.set('Search failed. Check that the backend, yt-dlp and spotDL are available.');
        this.loading.set(false);
      },
    });
  }

  add(hit: SearchResult): void {
    if (!this.device || this.locked(hit.url)) return;
    this.setRow(hit.url, 'starting');
    this.api.createDownload(hit.url, this.device, null).subscribe({
      next: job => {
        this.setRow(hit.url, job);
        this.api.watch(job.id).subscribe({
          next: update => this.setRow(hit.url, update),
          error: () => this.api.job(job.id).subscribe(update => this.setRow(hit.url, update)),
        });
      },
      error: () => this.setRow(hit.url, 'error'),
    });
  }

  locked(url: string): boolean {
    const row = this.rows()[url];
    if (row === undefined || row === 'error') return false;
    return row === 'starting' || ACTIVE.includes(row.status) || row.status === 'COMPLETED';
  }

  label(url: string): string {
    const row = this.rows()[url];
    if (row === undefined) return 'Add to USB';
    if (row === 'starting') return 'Starting…';
    if (row === 'error') return 'Failed · retry';
    if (row.status === 'COMPLETED') return 'On USB ✓';
    if (row.status === 'FAILED' || row.status === 'CANCELLED') return 'Failed · retry';
    return row.status.charAt(0) + row.status.slice(1).toLowerCase();
  }

  progress(url: string): number {
    const row = this.rows()[url];
    if (row === undefined || row === 'starting' || row === 'error' || !row.items.length) return 0;
    if (row.status === 'COMPLETED') return 0;
    return row.items.reduce((sum, item) => sum + item.progress, 0) / row.items.length;
  }

  duration(seconds?: number): string {
    if (seconds === undefined || seconds === null) return '—';
    return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  }

  private setRow(url: string, state: RowState): void {
    this.rows.update(rows => ({ ...rows, [url]: state }));
  }
}
