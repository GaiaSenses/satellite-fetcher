from satfetcher.products.fire.model import FireResponse
from satfetcher.products import sources
from satfetcher.products import utils
from satfetcher.products.base import Processor

import itertools


class FireProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.dist = dist
        self._cnt = itertools.count()

    def _getcache(self):
        return self.cache.geoget('fire', self.lat, self.lon, self.dist)

    def _savecache(self, lat, lon):
        expire = 30 * 60 # 30min
        self.cache.geoset('fire', [lon, lat, next(self._cnt)], expire)

    def process(self):
        location = self.get_location()
        out = {
            'count': 0,
            'events': [],
            'city': location['name'],
            'state': location['state'],
        }

        cached = self._getcache()
        if cached is not None:
            for _, dist, coord in cached:
                lon, lat = coord
                out['events'].append({
                    'lat': lat,
                    'lon': lon,
                    'dist': round(dist, 2),
                })
        else:
            samples = self.source.get()

            for _, sample in samples.body.iterrows():
                orig = [self.lat, self.lon]
                fire = [sample['latitude'], sample['longitude']]
                confidence = sample['confidence']

                if confidence != 'l':
                    self._savecache(lat=fire[0], lon=fire[1])
                    dist = utils.distance(orig, fire)
                    if dist <= self.dist:
                        out['events'].append({
                            'lat': fire[0],
                            'lon': fire[1],
                            'dist': round(dist, 2),
                        })

        out['count'] = len(out['events'])
        return FireResponse(**out)
