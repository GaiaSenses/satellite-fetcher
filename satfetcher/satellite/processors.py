from netCDF4 import Dataset

from . import utils
from . import sources


class Processor:
    def __init__(self, source: sources.DataSource, lat: float, lon: float):
        self.source = source
        self.lat = lat
        self.lon = lon
        self.geo = sources.OWGeocodingSource()

    def process(self):
        pass

    def get_location(self):
        data = self.geo.get(self.lat, self.lon)
        return data.body[0]


class RainfallProcessor(Processor):
    def __init__(self, source: sources.DataSource, *args, **kwargs):
        super().__init__(source, *args, **kwargs)

    def process(self):
        location = self.get_location()
        data = self.source.get(lat=self.lat, lon=self.lon)

        def map_weather(weather: list):
            def fn(w):
                return { 'main': w['main'], 'description': w['description'], 'icon': w['icon'] }
            return map(fn, weather)

        def filter_main(main: dict):
            def fn(m):
                k, _ = m
                return k not in ['temp_min', 'temp_max', 'sea_level']
            return filter(fn, main.items())

        out = {
            'lat': data.body['coord']['lat'],
            'lon': data.body['coord']['lon'],
            'rain': data.body.get('rain', {}),
            'wind': data.body.get('wind', {}),
            'main': dict(filter_main(data.body['main'])),
            'weather': list(map_weather(data.body['weather'])),
            'clouds': data.body['clouds']['all'],
            'visibility': data.body['visibility'],
            'city': location['name'],
            'state': location['state'],
        }
        return out


class LightningProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float = 50.0, *args, **kwargs):
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
        return out


class FireProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float = 50.0, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self.dist = dist

    def process(self):
        location = self.get_location()
        samples = self.source.get()
        out = {
            'count': 0,
            'events': [],
            'city': location['name'],
            'state': location['state'],
        }

        for sample in samples.body:
            props = sample['properties']
            orig = [self.lat, self.lon]
            fire = [props['latitude'], props['longitude']]

            d = utils.distance(orig, fire)
            if d <= self.dist:
                out['events'].append({
                    'lat': fire[0],
                    'lon': fire[1],
                    'dist': round(d, 2),
                    'city': props['municipio'],
                    'state': props['estado']
                })

        out['count'] = len(out['events'])
        return out
