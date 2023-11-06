from netCDF4 import Dataset

from satfetcher.products.lightning.model import LightningResponse
from satfetcher.products import sources
from satfetcher.products import utils
from satfetcher.products.base import Processor


class LightningProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.dist = dist

    def process(self):
        location = self.get_location()
        samples = self.source.get(n=3)
        out = {
            'count': 0,
            'events': [],
            'city': location['name'],
            'state': location['state'],
        }

        for sample in samples:
            ds = Dataset('in-memory.nc', memory=sample.body)

            lats = ds.variables['flash_lat'][:]
            lons = ds.variables['flash_lon'][:]

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
