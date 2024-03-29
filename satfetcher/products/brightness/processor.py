from osgeo import gdal, osr

from satfetcher.products.brightness.model import BrightnessResponse
from satfetcher.products import sources
from satfetcher.products.base import Processor


class BrightnessTemperatureProcessor(Processor):
    def __init__(self, source: sources.DataSource, lat: float, lon: float):
        super().__init__(source, lat, lon)

    def process(self):
        location = self.get_location()
        temp = 0

        cached = self._getcache()
        if cached is not None:
            buf, transform = cached
            x, y = self._coord2idx([self.lat, self.lon], transform)
            temp = buf[y, x]
        else:
            sample = self.source.get(n=1)[0]

            buf, transform = self._reproject(sample.body)
            x, y = self._coord2idx([self.lat, self.lon], transform)

            # Cache results
            self._savecache(buf, transform)

            temp = buf[y, x]

        out = {
            'temp': round(temp, 2),
            'city': location['name'],
            'state': location['state']
        }
        return BrightnessResponse(**out)

    def _savecache(self, data, transform):
        expire = 30 * 60 # 30min
        self.cache.npset('brightness:buf', data, expire)
        self.cache.npset('brightness:transform', transform, expire)

    def _getcache(self):
        buf = self.cache.npget('brightness:buf')
        transform = self.cache.npget('brightness:transform')
        if buf is not None and transform is not None:
            return buf, transform
        else:
            return None

    def _reproject(self, data):
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

        # Delete in-memory files
        gdal.Unlink('/vsimem/file.nc')
        gdal.Unlink('/vsimem/fileret.nc')

        return sat_array, transform

    def _coord2idx(self, coord, transform):
        x = int((coord[1] - transform[0]) / transform[1])
        y = int((transform[3] - coord[0]) / -transform[5])
        return x, y
