import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-dashboard',
  imports: [RouterLink],
  template: `
    <section class="page-heading"><p class="eyebrow">Overview</p><h1>Good evening, Mauricio</h1><p class="muted">Your music workspace at a glance.</p></section>
    <div class="stats-grid"><article class="stat-card accent"><span>Current sync</span><strong>Ready</strong><small>USB destination available</small></article><article class="stat-card"><span>Tracks synced</span><strong>0</strong><small>This week</small></article><article class="stat-card"><span>Free space</span><strong>—</strong><small>Connect a device to begin</small></article></div>
    <section class="panel welcome"><div><p class="eyebrow">Start a new transfer</p><h2>Bring your collection with you</h2><p class="muted">Analyze a playlist, choose the tracks you want, and MusicSync will prepare them safely for your USB device.</p></div><a class="button primary" routerLink="/downloads">Analyze a source <span>→</span></a></section>
  `,
  styles: [`.welcome { display:flex; justify-content:space-between; align-items:end; gap:2rem; } @media(max-width:700px){.welcome{display:block}.welcome .button{margin-top:1.5rem}}`]
})
export class DashboardComponent {}
