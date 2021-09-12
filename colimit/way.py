# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.9, copyright Monday, 13 September 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import datetime

from .location import Location
from .speed import Speed


class Way(object):

    def __init__(self,
                 id: int = 0,
                 nodes: tuple = tuple(),
                 geometry: tuple = tuple(),
                 oneway: bool = False,
                 limit: float = None,
                 variable: bool = False,
                 conditional: bool = False,
                 tags: dict = dict(),
                 **kwargs
                 ):
        """ way segment storing geometry points and speed limit

        :param id: way identifier
        :param nodes: list of location identifier (node id)
        :param geometry: list of |Location| (matching _node_ list)
        :param oneway: :class:`bool` if way is oneway
        :param limit: speed limit value as |Speed| with

                * -1 means no limit information
                * 0 means no limit

        :param variable: :class:`bool` if speed limit may vary by signal
        :param conditional: :class:`bool` if speed limit depends on time
            or weather conditions
        :param tags: dictionary of tags
            (as given by `Overpass-API` (OpenStreetMap),
            see: http://overpass-api.de)
        :param kwargs: additional or alternative arguments,
                e.g. _locations_ for _geometry_ or _maxspeed_ for _limit_.
        """
        nodes = tuple(int(n) for n in nodes)
        geometry = geometry or kwargs.get('locations', tuple())
        geometry = tuple(
            g if isinstance(g, Location) else Location(**g) for g in geometry)
        if geometry and nodes:
            self._validate_geometry(nodes, geometry)
        self._id = id
        self._nodes = nodes
        self._geometry = geometry
        self._tags = tags or dict()
        self._oneway = oneway
        if limit is None:
            limit = kwargs.get('maxspeed', -1.0)
        self._limit = Speed(float(limit))
        self._variable = variable
        self._conditional = conditional
        self._boundary = ()

    @staticmethod
    def _validate_geometry(nodes, geometry):
        # value must be list of Coordinates objects
        # in same order as self.node dicts
        for n, g in zip(nodes, geometry):
            if g.id and not int(n) == g.id:
                raise ValueError('Geometries must meet order of nodes')

    @property
    def geometry(self):
        """ geometry as a list of locations """
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        # geometry can only be set once
        if self._geometry:
            raise ValueError('Geometries can only be set once.')
        # validate geometries
        self._validate_geometry(self._nodes, value)
        self._geometry = value

    @property
    def id(self):
        """ way identifier """
        return self._id

    @property
    def nodes(self):
        """ nodes as a list of location identifier """
        return self._nodes

    @property
    def limit(self):
        """ speed limit with -1 as no limit information and 0 as no limit """
        return self._limit

    @property
    def oneway(self):
        """ `True` if lane is only oneway """
        return self._oneway

    @property
    def variable(self):
        """ `True` if _limit_ is variable over time, e.g. by a signal """
        return self._variable

    @property
    def conditional(self):
        """ `True` if _limit_ is conditional, i.e depends on time or weather """
        return self._conditional

    @property
    def boundary(self):
        """ bounding locations south/west and north/east """
        if not self._boundary:
            self._boundary = Location.boundary(*self.geometry)
        return self._boundary

    @property
    def center(self):
        """ center location of bounding box """
        return Location.center(*self._boundary)

    @property
    def diameter(self):
        """ south-to-north and west-to-east diameter of bounding box """
        return Location.diameter(*self.boundary)

    @property
    def length(self):
        """ length of way """
        length = 0.0
        for s, e in zip(self.geometry[:-1], self.geometry[1:]):
            length += s.dist(e)
        return length

    @property
    def duration(self):
        duration = datetime.timedelta()
        for s, e in zip(self.geometry[:-1], self.geometry[1:]):
            duration += e.time - s.time
        return duration

    @property
    def avg_speed(self):
        if self.duration:
            return Speed(self.length / self.duration.total_seconds())
        return 0.0

    @property
    def _dict(self):
        # assert kwargs == Way(**kwargs)._dict()
        d = dict()
        d['id'] = self.id
        d['oneway'] = self.oneway
        d['variable'] = self.variable
        d['conditional'] = self.conditional
        d['limit'] = float(self.limit)
        d['geometry'] = tuple({'latitude': float(g.latitude),
                               'longitude': float(g.longitude)
                               } for g in self.geometry)
        return d

    @property
    def json(self):
        """ dictionary of serializable instance properties """
        return self._dict

    def __contains__(self, item):
        # only not crossing date line
        # todo: handle date line boundaries
        # or see if item is node?
        if isinstance(item, Way):
            return item.geometry in self
        if isinstance(item, (tuple, list)):
            return any(i in self for i in item)
        if isinstance(item, Location):
            sw, ne = self.boundary
            return sw.latitude <= item.latitude <= ne.latitude \
                   and sw.longitude <= item.longitude <= ne.longitude
        return False

    def __str__(self):
        way = "Way(%d):" % self._id
        if self.geometry:
            vals = str(self.geometry[0]), str(self.geometry[-1])
            from_to = "\n from %s\n to   %s" % vals
        else:
            from_to = ""
        if float(self._limit) < 0.0:
            max_speed = "  no limit information"
        elif self._limit:
            max_speed = " limit of %s" % str(Speed(self._limit))
        else:
            max_speed = " no limit"
        return way + max_speed + from_to

    def __repr__(self):
        return "Way(%d)" % self._id

    def __eq__(self, other):
        return self.json == other.json

    def __hash__(self):
        return hash(str(self.json))
