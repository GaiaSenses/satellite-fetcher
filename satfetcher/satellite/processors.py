from netCDF4 import Dataset

from . import utils
from . import sources


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

            for (lat, lon) in zip(lats, lons):
                d = utils.distance([self.lat, self.lon], [lat, lon])
                if d <= 10000.0:
                    out.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'dist': round(d, 2)
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
            if d <= 50000.0:
                out.append({
                    'lat': fire[0],
                    'lon': fire[1],
                    'dist': round(d, 2),
                    'city': props['municipio'],
                    'state': props['estado']
                })

        return out
