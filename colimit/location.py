# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.8, copyright Tuesday, 31 August 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import datetime
from math import pi, sqrt, sin, cos, radians, degrees, asin, acos

from .speed import Speed

__all__ = 'Location',

EARTH_RADIUS = 6378137.

_cap = (lambda x: max(-1.0, min(x, 1.0)))


class Location(object):

    @staticmethod
    def xy(latitude, longitude, distance, direction):
        """ function to transform location coordinate
            with distance and direction
            into location coordinate (by default as planar geometry)

        :param latitude: location latitude in degrees
        :param longitude: location longitude in degrees
        :param distance: distance in meters
        :param direction: direction in degrees north
        :return: (latitude, longitude)
        """
        phi = radians(90 - direction)
        w = latitude + degrees(distance * cos(phi) / EARTH_RADIUS)
        z = longitude + degrees(distance * sin(phi) / EARTH_RADIUS)
        return w, z

    @staticmethod
    def polar(latitude, longitude, lat, lon):
        """ function to transform two location coordinate
            into distance and direction (by default as planar geometry)

        :param latitude: first location latitude in degrees
        :param longitude: first location longitude in degrees
        :param lat: second location latitude in degrees
        :param lon: second location longitude in degrees
        :return: (distance, direction)
        """
        dx = radians(lat - latitude) * EARTH_RADIUS
        dy = radians(lon - longitude) * EARTH_RADIUS
        r = sqrt(dx ** 2 + dy ** 2)
        a = degrees(acos(_cap(dx / r))) if r else 0.0
        a = 90 - a if 0 < dy else 90 + a
        a = a if 0. <= a else 360.0 + a
        return r, a

    def __init__(self,
                 latitude: float = 0.0,
                 longitude: float = 0.0,
                 speed: Speed = 0.0,
                 direction: float = 0.0,
                 timedelta: datetime.timedelta = None,
                 time: datetime.datetime = None,
                 id: int = 0,
                 **kwargs):
        """ point on earth with time, speed and direction

        :param latitude:
            `latitude coordinate <https://en.wikipedia.org/wiki/Latitude>`_
             (between -90 and 90 degrees)
        :param longitude:
            `longitude coordinate <https://en.wikipedia.org/wiki/Longitude>`_
            (between -180 and 180 degrees)
        :param speed: speed value (as |Speed|)
        :param direction: heading direction or
            `cardinal direction
            <https://en.wikipedia.org/wiki/Cardinal_direction>`_
            in degrees (clockwise between 0 and 360 degrees)
            from north=0.0 to east=90.0 and south=180.0 to west=270.0
        :param timedelta: time period (as :class:`datetime.timedelta`)
                which can be used to derive a distance by
                |Location().speed| * |Location().timedelta|
        :param time: timestamp (as :class:`datetime.datetime`)
        :param id: object identifier (as :class:`int`)
        :param kwargs: additional or alternative arguments,
                e.g. **lat** for **latitude**, **lon** for **longitude**,
                **spd** for **speed** and **dir** for **direction**.


        some transformations
        (|Location().dist()|, |Location().diff()|, |Location().next()|)
        makes use of geometry class properties

            |Location.polar()| and |Location.xy()|

        which sets the underlying geometry,
        i.e the local maps from tangent space
        (tangent vectors given as |Location|
        with **speed**, **direction** and **timedelta**
        at the point of **latitude** and **longitude**)
        to the earth sphere
        (points on the sphere given as |Location|
        with only **latitude** and **longitude**).

        """
        self._latitude = latitude or kwargs.get('lat', 0.0)
        self._longitude = longitude or kwargs.get('lon', 0.0)
        self._speed = speed or kwargs.get('spd', 0.0)
        self._direction = direction or kwargs.get('dir', 0.0)
        if time is None:
            time = datetime.datetime.now()
        self._time = time
        if timedelta is None:
            timedelta = datetime.timedelta()
        if not isinstance(timedelta, datetime.timedelta):
            timedelta = datetime.timedelta(seconds=float(timedelta))
        self._timedelta = timedelta
        self._id = id

    @property
    def id(self):
        """ location identifier (node id) """
        return self._id

    @property
    def latitude(self):
        """ latitude in degrees """
        return self._latitude

    @property
    def longitude(self):
        """ longitude in degrees """
        return self._longitude

    @property
    def coordinate(self):
        """ pair tuple (|Location().latitude|, |Location().longitude|) """
        return self._latitude, self._longitude

    @property
    def speed(self):
        """ speed value in mps """
        return Speed(self._speed)

    @property
    def direction(self):
        """ direction in degrees north """
        return self._direction

    @property
    def time(self):
        """ time value """
        return self._time

    @property
    def timedelta(self):
        """ timedelta value """
        return self._timedelta

    @property
    def _dict(self):
        kwargs = dict()
        kw = 'id',
        for k in kw:
            kwargs[k] = int(getattr(self, k, 0.0))
        kw = 'latitude', 'longitude', 'speed', 'direction'
        for k in kw:
            kwargs[k] = float(getattr(self, k, 0.0))
        kw = 'time', 'timedelta'
        for k in kw:
            kwargs[k] = (getattr(self, k, 0.0))
        return kwargs

    @property
    def json(self):
        """ dictionary of serializable instance properties """
        kwargs = self._dict
        kw = 'time', 'timedelta'
        for k in kw:
            kwargs[k] = str(kwargs[k])
        return kwargs

    # -- public methods ---

    @staticmethod
    def boundary(*locations, radius=0.0):
        """ pair tuple of south/west and north/east bounding location

        :param locations: locations to derive boundary from
        :param radius: radius of each location in locations
                which extends the boundary
        :return: (|Location|, |Location|)

        """
        if locations:
            south = min(g.latitude for g in locations)
            west = min(g.longitude for g in locations)
            north = max(g.latitude for g in locations)
            east = max(g.longitude for g in locations)
            south_west = Location(south, west).next(radius, 45 + 180)
            north_east = Location(north, east).next(radius, 45)
            return south_west, north_east

    @staticmethod
    def center(*locations, radius=0.0):
        """ center of locations boundary

        :param locations:  locations to derive center from
        :param radius: radius of each location in locations
                which extends the boundary
        :return: |Location|
        """
        south_west, north_east = Location.boundary(*locations, radius=radius)
        lat = (north_east.latitude - south_west.latitude)/2
        lon = (north_east.longitude - south_west.longitude)/2
        return Location(south_west.latitude + lat, south_west.longitude + lon)

    @staticmethod
    def diameter(*locations, radius=0.0):
        south_west, north_east = Location.boundary(*locations, radius=radius)
        south_east = Location(south_west.latitude, north_east.longitude)
        north_west = Location(north_east.latitude, south_west.longitude)
        dx, _ = Location.polar(*south_west.coordinate, *south_east.coordinate)
        dy, _ = Location.polar(*south_west.coordinate, *north_west.coordinate)
        return dx, xy

    def clone(self, **kwargs):
        """ clones a |Location| object with optional argument overwrites

        :param kwargs: optional Location argument overwrites
        :return: |Location|
        """
        self_dict = self._dict
        self_dict.update(kwargs)
        return self.__class__(**self_dict)

    def dist(self, other=None):
        """ distance to another |Location| object

        :param other: location (optional with default |Location()|
        :return: :class:`float` (distance in meters)

        transformation makes use of geometry class property
        |Location.polar()| which sets the underlying geometry
        """
        other = self.__class__() if other is None else other
        return self.__class__.polar(*self.coordinate, *other.coordinate)[0]

    def diff(self, other, **kwargs):
        """ difference to another location
            expressed as |Location| with speed, direction and timedelta

        :param other: the other location
        :param kwargs: optional Location argument overwrites
            (except **speed**, **direction** and **timedelta**)
        :return: |Location|

        |Location.diff()| is somehow the inverse to |Location.next()|
        since

        .. code-block:: python

            >>> from colimit import Location
            >>> h_da = colimit.Location(latitude=49.867219, longitude=8.638495)
            >>> tu_da = colimit.Location(latitude=49.875148, longitude=8.658122)
            >>> delta = h_da.diff(tu_da)
            >>> h_da.coordinate == delta.coordinate
            True
            >>> delta.next().coordinate == tu_da.coordinate
            True

        Note the transformation makes use of geometry class property
        |Location.polar()| which sets the underlying geometry
        """
        # build location to get in time from self to other
        dist, drc = self.__class__.polar(*self.coordinate, *other.coordinate)
        td = other.time - self.time
        spd = dist / td.total_seconds() if td else 0.0
        return self.clone(speed=spd, direction=drc, timedelta=td, **kwargs)

    def next(self, radius=None, direction=None, timedelta=None, **kwargs):
        """ location in given distance and direction

        :param radius: distance in meters
            (optional with default |Location().speed| * **timedelta**)
        :param direction: direction in cardinal degrees
            (optional with default |Location().direction|)
        :param timedelta: time period of motion
            (optional with default |Location().timedelta|)
        :param kwargs: optional Location argument overwrites
            (except **latitude**, **longitude** and **time**)
        :return: |Location|

        transformation makes use of geometry class property
        |Location.xy()| which sets the underlying geometry
        """
        if timedelta is None:
            timedelta = self.timedelta
        if isinstance(timedelta, datetime.timedelta):
            timedelta = timedelta.total_seconds()
        if radius is None:
            radius = self.speed.mps * timedelta
        if direction is None:
            direction = self.direction
        lat, lon = self.__class__.xy(*self.coordinate, radius, direction)
        tm = self.time + datetime.timedelta(seconds=timedelta)
        return self.clone(latitude=lat, longitude=lon, time=tm, **kwargs)

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
        return any((self.latitude, self.longitude,
                    self.speed, self.direction, self.timedelta))

    def __eq__(self, other):
        a = self.json
        o = other.json
        a.pop('time')
        o.pop('time')
        return a == o
