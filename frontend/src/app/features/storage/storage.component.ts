import { Component, inject, signal } from '@angular/core';
import { MusicSyncApiService, StorageDevice } from '../../core/services/music-sync-api.service';

@Component({
  standalone: true,
  selector: 'app-storage',
  template: `<section class="page-heading"><p class="eyebrow">Storage</p><h1>Destinations</h1><p class="muted">Connected devices available for your music.</p></section><div class="panel"><div class="panel-title"><h2>Devices</h2><button class="button subtle" (click)="load()">Refresh</button></div>@if (devices().length === 0) {<div class="empty"><span class="empty-icon">⌁</span><h3>No devices detected</h3><p class="muted">Connect a USB drive and refresh to see it here.</p></div>} @else {<div class="device-list">@for (device of devices(); track device.id) {<article class="device"><div class="device-icon">USB</div><div><strong>{{ device.volume_label }}</strong><p class="muted">{{ device.filesystem }} · {{ device.mount_point }}</p></div><span class="device-space">{{ format(device.free_space) }} free</span></article>}</div>}</div>`,
  styles: [`.panel-title{display:flex;justify-content:space-between;align-items:center}.device-list{display:grid;gap:1rem}.device{display:flex;align-items:center;gap:1rem;border:1px solid var(--line);border-radius:14px;padding:1rem}.device-icon{background:var(--mint);color:var(--ink);font-size:.7rem;font-weight:800;padding:.55rem;border-radius:8px}.device-space{margin-left:auto;color:var(--muted);font-size:.9rem}.empty{text-align:center;padding:4rem 1rem}.empty-icon{font-size:3rem;color:var(--mint)}`]
})
export class StorageComponent {
  private readonly api = inject(MusicSyncApiService);
  readonly devices = signal<StorageDevice[]>([]);
  constructor() { this.load(); }
  load(): void { this.api.devices().subscribe({ next: value => this.devices.set(value), error: () => this.devices.set([]) }); }
  format(bytes: number): string { return `${(bytes / 1_000_000_000).toFixed(1)} GB`; }
}
