import math

# WGS84 equatorial radius, in meters
EARTH_RADIUS = 6378137.0

def sign(x):
    return 1 if x >= 0 else -1


def distance(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [*a, *b])

    k1 = math.sin((lat2 - lat1) / 2.0) ** 2
    k2 = math.sin((lon2 - lon1) / 2.0) ** 2
    k3 = math.cos(lat1) * math.cos(lat2)

    return 2 * EARTH_RADIUS * math.asin(math.sqrt(k1 + k2*k3))


def translate(a, d):
    dlat, dlon = d[0], d[1]
    lat, lon = a[0], a[1]

    k1 = math.cos(math.radians((dlat * 180) / (EARTH_RADIUS * math.pi)))
    k2 = math.cos(math.radians((dlon * 180) / (EARTH_RADIUS * math.pi)))

    lat += sign(dlat) * math.degrees(math.acos(k1))
    lon += sign(dlon) * math.degrees(math.acos(k2))
    return [lat, lon]


def to_dms(a):
    def convert(x):
        s = sign(x)
        deg = abs(math.trunc(x))
        min = math.trunc((x - deg) * 60)
        sec = (x - deg - min/60) * 3600
        return [s * deg, min, sec]

    return [convert(a[0]), convert(a[1])]

def from_dms(deg, min, sec):
    s = sign(deg)
    deg, min, sec = abs(deg), abs(min), abs(sec)
    return s * (deg + (min/60.0) + (sec/3600.0))
