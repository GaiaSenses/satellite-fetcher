from netCDF4 import Dataset

from . import utils
from . import sources

# distance in metres
LIGHTNING_MAX_DIST = 50000
FIRE_MAX_DIST = 50000

class Processor:
    def __init__(self, source: sources.DataSource, lat: float, lon: float):
        self.source = source
        self.lat = lat
        self.lon = lon

    def process(self):
        pass


class RainfallProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):
        data = self.source.get(lat=self.lat, lon=self.lon)
        out = {
            'lat': data.body['coord']['lat'],
            'lon': data.body['coord']['lon'],
            'rain': data.body.get('rain', {}),
            'wind': data.body.get('wind', {})
        }
        return out


class LightningProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):
        samples = self.source.get(n=3)
        out = []

        for sample in samples:
            ds = Dataset('in-memory.nc', memory=sample.body)

            lats = ds.variables['flash_lat'][:]
            lons = ds.variables['flash_lon'][:]

            distances = utils.distance([lats, lons], [self.lat, self.lon])
            dist_mask = distances <= LIGHTNING_MAX_DIST

            for dist, lat, lon in zip(distances[dist_mask], lats[dist_mask], lons[dist_mask]):
                out.append({
                    'lat': float(lat),
                    'lon': float(lon),
                    'dist': round(float(dist), 2)
                })

            ds.close()

        return out


class FireProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self):
        samples = self.source.get()
        out = []

        for sample in samples.body:
            props = sample['properties']
            orig = [self.lat, self.lon]
            fire = [props['latitude'], props['longitude']]

            d = utils.distance(orig, fire)
            if d <= FIRE_MAX_DIST:
                out.append({
                    'lat': fire[0],
                    'lon': fire[1],
                    'dist': round(d, 2),
                    'city': props['municipio'],
                    'state': props['estado']
                })

        return out
