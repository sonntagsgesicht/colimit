# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


from datetime import datetime, timedelta
from math import pi, sqrt, sin, cos, radians, degrees, asin, acos

from .speed import Speed

__all__ = 'Location',

EARTH_RADIUS = 6378137.

_cap = lambda x: max(-1.0, min(x, 1.0))


def _planar_xy(x, y, r, a):
    phi = radians(90 - a)
    w = x + degrees(r * cos(phi) / EARTH_RADIUS)
    z = y + degrees(r * sin(phi) / EARTH_RADIUS)
    return w, z


def _planar_polar(x, y, w, z):
    dx = radians(w - x) * EARTH_RADIUS
    dy = radians(z - y) * EARTH_RADIUS
    r = sqrt(dx ** 2 + dy ** 2)
    a = degrees(acos(_cap(dx / r))) if r else 0.0
    a = 90 - a if 0 < dy else 90 + a
    a = a if 0. <= a else 360.0 + a
    return r, a


class Location(object):

    def __init__(self,
                 latitude: float = 0.0,
                 longitude: float = 0.0,
                 speed: Speed = 0.0,
                 direction: float = 0.0,
                 time: datetime = datetime.now(),
                 timedelta: timedelta = timedelta(),
                 id: int = 0,
                 **kwargs):
        '''

        :param latitude: in degrees
        :param longitude: in degrees
        :param speed: in mps
        :param direction: in degrees north
        :param time: as datetime
        :param timedelta: as timedelta
        :param id: name
        :param kwargs: dupes as 'lat' or 'lon'
        '''
        self._latitude = latitude or kwargs.get('lat', 0.0)
        self._longitude = longitude or kwargs.get('lon', 0.0)
        self._speed = speed or kwargs.get('spd', 0.0)
        self._direction = direction or kwargs.get('dir', 0.0)
        self._time = time
        self._timedelta = timedelta
        self._id = id

        self._polar, self._xy = _planar_polar, _planar_xy
        geometry = kwargs.get('geometry', None)
        if geometry is not None:
            self._polar, self._xy = geometry

    @property
    def id(self):
        return self._id

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def coordinate(self):
        return self._latitude, self._longitude

    @property
    def speed(self):
        return Speed(self._speed)

    @property
    def direction(self):
        return self._direction

    @property
    def time(self):
        return self._time

    @property
    def timedelta(self):
        return self._timedelta

    @property
    def geometry(self):
        return self._polar, self._xy

    @property
    def dict(self):
        kwargs = dict()
        kw = 'id',
        for k in kw:
            kwargs[k] = int(getattr(self, k, 0.0))
        kw = 'latitude', 'longitude', 'speed', 'direction'
        for k in kw:
            kwargs[k] = float(getattr(self, k, 0.0))
        kw = 'time', 'timedelta', 'geometry'
        for k in kw:
            kwargs[k] = (getattr(self, k, 0.0))
        return kwargs

    @property
    def json(self):
        kwargs = self.dict
        kw = 'time', 'timedelta'
        for k in kw:
            kwargs[k] = str(kwargs[k])
        kwargs.pop('geometry')
        return kwargs

    # -- public methods ---

    @staticmethod
    def boundary(*locations, radius=0.0):
        if locations:
            south = min(g.latitude for g in locations)
            west = min(g.longitude for g in locations)
            north = max(g.latitude for g in locations)
            east = max(g.longitude for g in locations)
            south_west = Location(south, west).next(radius, 45 + 180)
            north_east = Location(north, east).next(radius, 45)
            return south_west, north_east

    def dist(self, other=None):
        other = self.__class__() if other is None else other
        return self._polar(*self.coordinate, *other.coordinate)[0]

    def diff(self, other):
        # build location to get in time from self to other
        dist, direction = self._polar(*self.coordinate, *other.coordinate)
        time_diff = other.time - self.time
        sec = time_diff.total_seconds()
        cls, kwargs = self.__class__, self.dict
        kwargs['speed'] = dist / sec if sec else 0.0
        kwargs['direction'] = direction
        kwargs['timedelta'] = time_diff
        return cls(**kwargs)

    def next(self, radius=None, direction=None, next_id=0):
        if radius is None:
            radius = self.speed.mps * self.timedelta.total_seconds()
        if direction is None:
            direction = self.direction
        lat, lon = self._xy(*self.coordinate, radius, direction)
        cls, kwargs = self.__class__, self.dict
        if id:
            kwargs['id'] = next_id
        kwargs['latitude'] = lat
        kwargs['longitude'] = lon
        kwargs['time'] += self.timedelta
        return cls(**kwargs)

    # --- private methods ---

    def __str__(self):
        ret = "Location at (%08.6f,%009.6f)" % (self._latitude, self._longitude)
        if self._speed or self._direction:
            ret += ' with speed %0.1f km/h in direction %0.2f°' \
                   % (self.speed.kmh, self._direction)
        if self._time:
            ret += ' at %s' % self._time.strftime('%y-%m-%d:%H-%M-%S')
        if self._timedelta:
            ret += ' plus %0.3fs' % self._timedelta.total_seconds()
        return ret

    def __repr__(self):
        return str(self)

    def __next__(self):
        return self.next()

    def __bool__(self):
        return any((self.latitude, self.longitude, self.speed, self.direction))

    def __eq__(self, other):
        return self.dict == other.dict
