from satfetcher.products.fire.model import FireResponse
from satfetcher.products import sources
from satfetcher.products import utils
from satfetcher.products.base import Processor


class FireProcessor(Processor):
    def __init__(self, source: sources.DataSource, dist: float, *args, **kwargs):
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

        for _, sample in samples.body.iterrows():
            orig = [self.lat, self.lon]
            fire = [sample['latitude'], sample['longitude']]
            confidence = sample['confidence']

            d = utils.distance(orig, fire)
            if confidence != 'l' and d <= self.dist:
                out['events'].append({
                    'lat': fire[0],
                    'lon': fire[1],
                    'dist': round(d, 2),
                })

        out['count'] = len(out['events'])
        return FireResponse(**out)
