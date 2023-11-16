class InvalidLocation(Exception):
    def __init__(self, lat, lon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lat = lat
        self.lon = lon
