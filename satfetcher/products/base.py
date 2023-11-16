from satfetcher.errors import InvalidLocation
from satfetcher.products import sources
from satfetcher.products.cache import Cache

class Processor:
    def __init__(self, source: sources.DataSource, lat: float, lon: float):
        self.source = source
        self.lat = lat
        self.lon = lon
        self.geo = sources.OWGeocodingSource()
        self.cache = Cache()

    def process(self):
        pass

    def get_location(self):
        data = self.geo.get(self.lat, self.lon)

        if not data.body:
            raise InvalidLocation(self.lat, self.lon)

        return data.body[0]
