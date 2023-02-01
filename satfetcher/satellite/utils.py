import math
import numpy as np

# WGS84 equatorial radius, in meters
EARTH_RADIUS = 6378137.0

def sign(x):
    if type(x) != np.ndarray:
        res = np.array(x, copy=True)
    else:
        res = np.copy(x)

    res[res < 0] = -1
    res[res >= 0] = 1

    return res


def distance(a, b):
    lat1, lon1, lat2, lon2 = map(np.radians, [*a, *b])

    k1 = np.sin((lat2 - lat1) / 2.0) ** 2
    k2 = np.sin((lon2 - lon1) / 2.0) ** 2
    k3 = np.cos(lat1) * np.cos(lat2)

    return 2 * EARTH_RADIUS * np.arcsin(np.sqrt(k1 + k2*k3))

def translate(a, d):
    dlat, dlon = d[0], d[1]
    lat, lon = a[0], a[1]

    k1 = np.cos(np.radians((dlat * 180) / (EARTH_RADIUS * np.pi)))
    k2 = np.cos(np.radians((dlon * 180) / (EARTH_RADIUS * np.pi)))

    lat += sign(dlat) * np.degrees(np.arccos(k1))
    lon += sign(dlon) * np.degrees(np.arccos(k2))
    return [lat, lon]


def to_dms(a):
    def convert(x):
        s = sign(x)
        deg = np.abs(np.trunc(x))
        min = np.trunc((x - deg) * 60)
        sec = (x - deg - min/60) * 3600
        return np.array([s * deg, min, sec])

    a0 = convert(a[0]).swapaxes(0, 1)
    a1 = convert(a[1]).swapaxes(0, 1)

    return [a0, a1]

def from_dms(deg, min, sec):
    s = np.sign(deg) or 1
    deg, min, sec = np.abs(deg), np.abs(min), np.abs(sec)
    return s * (deg + (min/60.0) + (sec/3600.0))
