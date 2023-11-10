from satfetcher.products.cache import Cache
from satfetcher.products.sources import GOESSource
from .processor import BrightnessTemperatureProcessor

class BrightnessTemperatureService:
    def __init__(self, lat, lon):
        self.source = GOESSource('ABI-L2-CMIPF', maxcache=10)
        self.processor = BrightnessTemperatureProcessor(self.source, lat, lon)
        self.cache = Cache()
        self.cache_name = 'brightness'

    def get(self):
        arr = self.cache.npget(self.cache_name)
        if arr is None:
            print('NPGET NONE: cache miss')
            return self.processor.process()

        return arr
