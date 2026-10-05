import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MusicSyncApiService, Analysis, Track } from '../../core/services/music-sync-api.service';

@Component({
  standalone: true, selector: 'app-downloads', imports: [FormsModule],
  template: `<section class="page-heading"><p class="eyebrow">Downloads</p><h1>New sync</h1><p class="muted">Analyze a source and choose what belongs on your device.</p></section><div class="panel source-panel"><label for="source">Source URL</label><div class="url-row"><input id="source" [(ngModel)]="url" placeholder="Paste a YouTube or playlist URL" (keyup.enter)="analyze()"><button class="button primary" (click)="analyze()" [disabled]="loading">{{ loading ? 'Analyzing…' : 'Analyze' }}</button></div>@if (error()) {<p class="error">{{ error() }}</p>}</div>@if (analysis(); as result) {<section class="panel"><div class="panel-title"><div><p class="eyebrow">{{ result.source }}</p><h2>Select tracks</h2></div><span class="pill">{{ selectedCount() }} selected</span></div><div class="track-list">@for (track of result.tracks; track track.id) {<label class="track"><input type="checkbox" [checked]="selected().has(track.id)" (change)="toggle(track)"><span class="track-art">♪</span><span class="track-info"><strong>{{ track.title }}</strong><small>{{ track.artist }}{{ track.album ? ' · ' + track.album : '' }}</small></span><span class="duration">{{ duration(track.duration_seconds) }}</span></label>}</div><div class="actions"><select [(ngModel)]="device"><option value="usb-1">Select destination</option><option value="usb-1">USB drive</option></select><button class="button primary" (click)="start()" [disabled]="selectedCount() === 0">Start sync <span>→</span></button></div>@if (message()) {<p class="success">{{ message() }}</p>}</section>}`,
  styles: [`.source-panel label{display:block;font-weight:700;margin-bottom:.6rem}.url-row{display:flex;gap:.75rem}.url-row input{flex:1}.track-list{margin-top:1.4rem}.track{display:flex;align-items:center;gap:1rem;padding:.9rem 0;border-bottom:1px solid var(--line);cursor:pointer}.track-art{display:grid;place-items:center;width:2.4rem;height:2.4rem;border-radius:8px;background:var(--mint);font-weight:800}.track-info{display:grid;gap:.2rem;flex:1}.track-info small,.duration{color:var(--muted)}.actions{display:flex;justify-content:flex-end;gap:.75rem;margin-top:1.4rem}.actions select{border:1px solid var(--line);border-radius:9px;padding:.7rem;background:var(--surface)}.error{color:#b33a36;margin-bottom:0}.success{color:#14734b}.panel-title{display:flex;justify-content:space-between;align-items:start}.pill{font-size:.75rem;padding:.35rem .65rem;border-radius:99px;background:var(--surface-2);color:var(--muted)}@media(max-width:650px){.url-row,.actions{display:grid}.url-row .button,.actions .button{width:100%}}`]
})
export class DownloadsComponent {
  private readonly api = inject(MusicSyncApiService);
  url = ''; device = 'usb-1'; loading = false;
  readonly analysis = signal<Analysis | null>(null); readonly error = signal(''); readonly message = signal(''); readonly selected = signal<Set<string>>(new Set());
  analyze(): void { if (!this.url.trim()) return; this.loading = true; this.error.set(''); this.message.set(''); this.api.analyze(this.url.trim()).subscribe({ next: result => { this.analysis.set(result); this.selected.set(new Set(result.tracks.map(track => track.id))); this.loading = false; }, error: () => { this.error.set('Could not analyze this source. Check the URL and try again.'); this.loading = false; } }); }
  toggle(track: Track): void {
    const ids = new Set(this.selected());
    if (ids.has(track.id)) {
      ids.delete(track.id);
    } else {
      ids.add(track.id);
    }
    this.selected.set(ids);
  }
  selectedCount(): number { return this.selected().size; }
  start(): void { this.api.createDownload(this.url, this.device, [...this.selected()]).subscribe({ next: job => this.message.set(`Job ${job.id.slice(0, 8)} created.`), error: () => this.error.set('Could not create the download job.') }); }
  duration(seconds?: number): string { if (seconds === undefined) return '—'; return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`; }
}
