# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


from .location import Location
from .speed import Speed


class Way(object):

    def __init__(self,
                 id: int = 0,
                 nodes: tuple = tuple(),
                 geometry: tuple = tuple(),
                 oneway: bool = False,
                 limit: Speed = None,
                 variable: bool = False,
                 conditional: bool = False,
                 tags: dict = dict(),
                 **kwargs
                 ):
        nodes = tuple(int(n) for n in nodes)
        geometry = tuple(
            g if isinstance(g, Location) else Location(**g) for g in geometry)
        if geometry and nodes:
            self._validate_geometry(nodes, geometry)
        self._id = id
        self._nodes = nodes
        self._geometry = geometry
        self._tags = tags or dict()
        self._oneway = oneway
        if not (limit is None or limit == -1.0):
            self._limit = Speed(limit)
        else:
            self._limit = limit
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
        return self._id

    @property
    def nodes(self):
        return self._nodes

    @property
    def limit(self):
        return self._limit

    @property
    def oneway(self):
        return self._oneway

    @property
    def variable(self):
        return self._variable

    @property
    def conditional(self):
        return self._conditional

    @property
    def boundary(self):
        if not self._boundary:
            self._boundary = Location.boundary(*self.geometry)
        return self._boundary

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
        if self._limit:
            max_speed = " limit of %0.f kmh" % self._limit.kmh
        else:
            max_speed = " no limit"
        return way + max_speed + from_to

    def __repr__(self):
        return "Way(%d)" % self._id

    def __eq__(self, other):
        return self.dict == other.dict

    def __hash__(self):
        return hash(str(self.dict))

    @property
    def dict(self):
        # assert kwargs == Way(**kwargs).dict()
        d = dict()
        d['id'] = self.id
        d['oneway'] = self.oneway
        d['variable'] = self.variable
        d['conditional'] = self.conditional
        d['limit'] = -1.0 if self.limit is None else float(self.limit)
        d['geometry'] = tuple({'latitude': float(g.latitude),
                               'longitude': float(g.longitude)
                               } for g in self.geometry)
        return d

    @property
    def json(self):
        return self.dict
