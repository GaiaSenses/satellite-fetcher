import abc
import json
import os
from datetime import datetime, timedelta
from urllib.request import urlopen

import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.config import Config


class DataSource(abc.ABC):
    @abc.abstractmethod
    def get(self, *args, **kwargs):
        pass


class GOESResponse:
    def __init__(self, key, date, body):
        self.key = key
        self.date = date
        self.body = body


class JSONResponse:
    def __init__(self, body):
        self.body = body

class CSVResponse:
    def __init__(self, body):
        self.body = body

class GOESSource(DataSource):
    def __init__(self, product):
        super().__init__()

        self._s3 = boto3.resource(
            's3', config=Config(signature_version=UNSIGNED))
        self._bucket = self._s3.Bucket('noaa-goes16')
        self._product = product

    def get(self, n=1, *args, **kwargs):
        latest = self._nlatest(n)
        res = []
        for resource in latest:
            obj = resource.get()
            response = GOESResponse(
                resource.key, resource.last_modified, obj['Body'].read())

            res.append(response)

        return res

    def _nlatest(self, n):
        res = []
        h = 0
        while len(res) < n:
            dt = datetime.utcnow() - timedelta(hours=h)
            prefix = self._prefix(dt)
            objects = list(self._bucket.objects.filter(Prefix=prefix))
            res += objects[(len(res) - n):]
            h += 1
        return res

    def _prefix(self, utc: datetime):
        year = utc.year
        day = utc.strftime('%j')
        hour = utc.hour
        return f'{self._product}/{year}/{day}/{hour}'


class FIRMSSource(DataSource):
    API_URL = 'https://firms.modaps.eosdis.nasa.gov/api/country/csv/{key}/VIIRS_NOAA20_NRT/BRA/1'
    API_KEY = os.getenv('FIRMS_API_KEY')

    def __init__(self):
        super().__init__()

    def get(self):
        with urlopen(self.API_URL.format(key=self.API_KEY)) as res:
            return CSVResponse(pd.read_csv(res))


class OWSource(DataSource):
    API_URL = 'https://api.openweathermap.org/data/2.5/weather?appid={key}&lat={lat}&lon={lon}&units=metric&lang=pt_br'
    API_KEY = os.getenv('OPENWEATHER_API_KEY')

    def __init__(self):
        super().__init__()

    def get(self, lat, lon, *args, **kwargs):
        with urlopen(self.API_URL.format(key=self.API_KEY, lat=lat, lon=lon)) as res:
            return JSONResponse(json.load(res))

class OWGeocodingSource(OWSource):
    API_URL = 'https://api.openweathermap.org/geo/1.0/reverse?appid={key}&lat={lat}&lon={lon}&limit=1'
