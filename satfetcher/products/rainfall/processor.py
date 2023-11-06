from satfetcher.products.rainfall.model import RainfallResponse
from satfetcher.products import sources
from satfetcher.products.base import Processor


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
            'rain': data.body.get('rain', None),
            'wind': data.body.get('wind', None),
            'main': dict(filter_main(data.body['main'])),
            'weather': list(map_weather(data.body['weather'])),
            'clouds': data.body['clouds']['all'],
            'visibility': data.body['visibility'],
            'city': location['name'],
            'state': location['state'],
        }
        return RainfallResponse(**out)
