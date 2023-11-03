from netCDF4 import Dataset
from osgeo import gdal, osr

from ..models.brightness import BrightnessResponse
from ..models.fire import FireResponse
from ..models.lightning import LightningResponse
from ..models.rainfall import RainfallResponse

from . import sources

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


class BrightnessTemperatureProcessor(Processor):
    def __init__(self, source: sources.DataSource, lat: float, lon: float):
        super().__init__(source, lat, lon)

    def process(self):
        location = self.get_location()
        samples = self.source.get(n=5)
        temp_sum = 0

        for sample in samples:
            temp_sum += self._temperature(sample.body)

        out = {
            'temp': round(temp_sum / len(samples), 2),
            'city': location['name'],
            'state': location['state']
        }
        return BrightnessResponse(**out)

    def _temperature(self, data):
        # Min lon, Min lat, Max lon, Max lat (values for Brazil)
        extent = [-74.0, -33, -34, 0.5]
        var = 'CMI'

        # Load input file
        gdal.FileFromMemBuffer('/vsimem/file.nc', data)
        img = gdal.Open('NETCDF:/vsimem/file.nc:' + var)

        # Read the header metadata
        metadata = img.GetMetadata()
        scale = float(metadata.get(var + '#scale_factor'))
        offset = float(metadata.get(var + '#add_offset'))
        undef = float(metadata.get(var + '#_FillValue'))
        dtime = metadata.get('NC_GLOBAL#time_coverage_start')

        # Load the data
        ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

        # Apply the scale, offset and convert to celsius
        ds = (ds * scale + offset) - 273.15

        # Read the original file projection and configure the output projection
        source_prj = osr.SpatialReference()
        source_prj.ImportFromProj4(img.GetProjectionRef())

        target_prj = osr.SpatialReference()
        target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

        # Reproject the data
        GeoT = img.GetGeoTransform()
        driver = gdal.GetDriverByName('MEM')
        raw = driver.Create('', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
        raw.SetGeoTransform(GeoT)
        raw.GetRasterBand(1).WriteArray(ds)

        # Define the parameters of the output file
        kwargs = {
            'format': 'MEM',
            'srcSRS': source_prj,
            'dstSRS': target_prj,
            'outputBounds': (extent[0], extent[3], extent[2], extent[1]),
            'outputBoundsSRS': target_prj,
            'outputType': gdal.GDT_Float32,
            'srcNodata': undef,
            'dstNodata': 'nan',
            'xRes': 0.02,
            'yRes': 0.02,
            'resampleAlg': gdal.GRA_NearestNeighbour
        }

        # Read number of cols and rows
        sat_data = gdal.Warp('/vsimem/fileret.nc', raw, **kwargs)
        ncol = sat_data.RasterXSize
        nrow = sat_data.RasterYSize

        # Load the data
        sat_array = sat_data.ReadAsArray(0, 0, ncol, nrow).astype(float)

        # Get geotransform
        transform = sat_data.GetGeoTransform()
        x = int((self.lon - transform[0]) / transform[1])
        y = int((transform[3] - self.lat) / -transform[5])

        # Get brightness temperature
        temp = sat_array[y,x]

        # Delete in-memory files
        gdal.Unlink('/vsimem/file.nc')
        gdal.Unlink('/vsimem/fileret.nc')

        return temp
