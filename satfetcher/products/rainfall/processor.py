from satfetcher.products.rainfall.model import RainfallResponse
from satfetcher.products import sources
from satfetcher.products.base import Processor

import itertools


class RainfallProcessor(Processor):
    def __init__(self, source: sources.DataSource, *args, **kwargs):
        super().__init__(source, *args, **kwargs)
        self._id = itertools.count()

    def _getcache(self, lat, lon):
        res = self.cache.geoget('rainfall', lat, lon)
        try:
            id, _, _ = res[0]
            return self.cache.get(id, convert=True)
        except:
            return None

    def _savecache(self, data: dict):
        lat, lon = data['lat'], data['lon']
        id = f'rainfall:{next(self._id)}'
        expire = 30 * 60 # 30min

        self.cache.geoset('rainfall', [lon, lat, id], expire)
        self.cache.set(id, data, expire)

    def process(self):
        cached = self._getcache(self.lat, self.lon)
        if cached is not None:
            return RainfallResponse(**cached)

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
        self._savecache(out)
        return RainfallResponse(**out)
