import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface Track {
  id: string;
  source_id: string;
  title: string;
  artist: string;
  album?: string;
  duration_seconds?: number;
  release_date?: string;
  original_url?: string;
}

export interface Analysis { source: string; tracks: Track[]; }
export interface DownloadItem {
  id: string;
  track_id: string;
  status: string;
  progress: number;
  error?: string;
  output_path?: string;
}
export interface DownloadJob {
  id: string;
  source_url: string;
  destination_device_id: string;
  status: string;
  total_items: number;
  completed_items: number;
  failed_items: number;
  items: DownloadItem[];
}
export interface StorageDevice {
  id: string;
  volume_label: string;
  mount_point: string;
  filesystem: string;
  total_space: number;
  free_space: number;
  is_available: boolean;
}

@Injectable({ providedIn: 'root' })
export class MusicSyncApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1';

  analyze(url: string): Observable<Analysis> {
    return this.http.post<Analysis>(`${this.baseUrl}/downloads/analyze`, { url });
  }

  createDownload(url: string, destinationDeviceId: string, trackIds: string[]): Observable<DownloadJob> {
    return this.http.post<DownloadJob>(`${this.baseUrl}/downloads`, {
      url, destination_device_id: destinationDeviceId, track_ids: trackIds
    });
  }

  job(id: string): Observable<DownloadJob> { return this.http.get<DownloadJob>(`${this.baseUrl}/downloads/${id}`); }
  cancel(id: string): Observable<DownloadJob> { return this.http.post<DownloadJob>(`${this.baseUrl}/downloads/${id}/cancel`, {}); }
  resume(id: string): Observable<DownloadJob> { return this.http.post<DownloadJob>(`${this.baseUrl}/downloads/${id}/resume`, {}); }

  /** Live job snapshots until the job reaches a terminal state. */
  watch(id: string): Observable<DownloadJob> {
    return new Observable<DownloadJob>(subscriber => {
      const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
      const socket = new WebSocket(`${scheme}://${location.host}/ws/downloads/${encodeURIComponent(id)}`);
      socket.onmessage = message => {
        const event = JSON.parse(message.data);
        if (event.job) subscriber.next(event.job as DownloadJob);
      };
      socket.onerror = () => subscriber.error(new Error('Progress connection failed'));
      socket.onclose = () => subscriber.complete();
      return () => socket.close();
    });
  }

  history(): Observable<DownloadJob[]> { return this.http.get<DownloadJob[]>(`${this.baseUrl}/downloads/history`); }
  devices(): Observable<StorageDevice[]> { return this.http.get<StorageDevice[]>(`${this.baseUrl}/storage/devices`); }
}
