import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { SearchComponent } from './search.component';
import { SearchResult } from '../../core/services/music-sync-api.service';

const HIT: SearchResult = {
  title: 'One More Time',
  artist: 'Daft Punk',
  url: 'https://www.youtube.com/watch?v=abc',
  source: 'youtube',
  duration_seconds: 322,
};

describe('SearchComponent', () => {
  function setup() {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    const component = TestBed.createComponent(SearchComponent).componentInstance;
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/v1/storage/devices').flush([
      { id: 'dev-1', volume_label: 'USB', mount_point: 'E:\\', filesystem: 'FAT32', total_space: 1, free_space: 1, is_available: true },
    ]);
    http.expectOne('/api/v1/search/capabilities').flush({ spotify_api: true });
    expect(component.spotifyApi()).toBe(true);
    return { component, http };
  }

  it('searches the chosen source and lists the results', () => {
    const { component, http } = setup();
    component.query = '  daft punk ';
    component.source = 'spotify';

    component.search();
    const request = http.expectOne(r => r.url === '/api/v1/search');
    expect(request.request.params.get('q')).toBe('daft punk');
    expect(request.request.params.get('source')).toBe('spotify');
    request.flush([HIT]);

    expect(component.results()).toEqual([HIT]);
    expect(component.duration(HIT.duration_seconds)).toBe('5:22');
    http.verify();
  });

  it('adds a result once and blocks repeated clicks while it is in flight', () => {
    const { component, http } = setup();

    component.add(HIT);
    component.add(HIT);

    const creates = http.match('/api/v1/downloads');
    expect(creates.length).toBe(1);
    expect(creates[0].request.body).toEqual({
      url: HIT.url,
      destination_device_id: 'dev-1',
      track_ids: null,
    });
    expect(component.label(HIT.url)).toBe('Starting…');
    expect(component.locked(HIT.url)).toBe(true);

    creates[0].error(new ProgressEvent('error'));
    expect(component.label(HIT.url)).toBe('Failed · retry');
    expect(component.locked(HIT.url)).toBe(false);
  });

  it('shows an error when the search request fails', () => {
    const { component, http } = setup();
    component.query = 'x';

    component.search();
    http.expectOne(r => r.url === '/api/v1/search').error(new ProgressEvent('error'));

    expect(component.error()).toContain('Search failed');
    expect(component.loading()).toBe(false);
  });
});
