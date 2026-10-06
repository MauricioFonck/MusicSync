import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { DownloadsComponent } from './downloads.component';
import { DownloadJob } from '../../core/services/music-sync-api.service';

describe('DownloadsComponent', () => {
  it('preselects the first detected device and averages item progress', () => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    const component = TestBed.createComponent(DownloadsComponent).componentInstance;
    const http = TestBed.inject(HttpTestingController);

    http.expectOne('/api/v1/storage/devices').flush([
      { id: 'dev-1', volume_label: 'USB', mount_point: 'E:\\', filesystem: 'FAT32', total_space: 1, free_space: 1, is_available: true },
    ]);

    expect(component.device).toBe('dev-1');
    const job = { items: [{ progress: 100 }, { progress: 50 }] } as DownloadJob;
    expect(component.progress(job)).toBe(75);
    http.verify();
  });
});
