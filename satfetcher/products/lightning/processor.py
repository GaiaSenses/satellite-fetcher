from netCDF4 import Dataset

from satfetcher.products.lightning.model import LightningResponse
from satfetcher.products import sources
from satfetcher.products import utils
from satfetcher.products.base import Processor

import itertools
import numpy as np


class LightningProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.dist = dist
        self._id = itertools.count()

    def _getcache(self):
        return self.cache.geoget('lightning', self.lat, self.lon, self.dist)

    def _savecache(self, lats, lons):
        expire = 30 * 60 # 30min
        labels = np.fromiter(self._id, dtype=float, count=lats.size)
        data = np.concatenate([lons[..., np.newaxis], lats[..., np.newaxis], labels[..., np.newaxis]], axis=-1)
        data = data.flatten()
        self.cache.geoset('lightning', data, expire)

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
            samples = self.source.get(n=3)
            for sample in samples:
                ds = Dataset('in-memory.nc', memory=sample.body)

                lats = ds.variables['flash_lat'][:]
                lons = ds.variables['flash_lon'][:]

                self._savecache(lats, lons)

                distances = utils.distance([lats, lons], [self.lat, self.lon])
                dist_mask = distances <= self.dist

                for dist, lat, lon in zip(distances[dist_mask], lats[dist_mask], lons[dist_mask]):
                    out['events'].append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'dist': round(float(dist), 2)
                    })

                ds.close()

        out['count'] = len(out['events'])
        return LightningResponse(**out)
