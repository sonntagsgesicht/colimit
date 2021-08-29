# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.7, copyright Sunday, 29 August 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


__all__ = 'Speed',

MPS = {
    'mps': 1.0,
    'kmh': 3.6,
    'mph': 2.23694,
    'fts': 3.28084,
    'knots': 1.94384
}


class Speed(object):

    def __init__(self,
                 speed: float = 0.0,
                 unit: str = 'mps'):
        """ extending :class:`float` by speed unit conversion

        :param speed:   absolut speed value
        :param unit:    unit of speed value (optional with default `mps`),
                        unit should be one of

                            * `mps` (meter per second)
                            * `kmh` (kilometer per hour)
                            * `mph` (miles per hour)
                            * `fts` (feet per second)
                            * `knots` (knots as 1.94384 `mps`

        |Speed()| instances can be added, subtracted, multiplied, divided
        and compared.

        """
        if not isinstance(speed, (float, Speed, int)):
            raise ValueError('Speed value must be float not %s' % type(speed))
        if unit in MPS:
            speed = float(speed) / MPS[unit]
        else:
            raise ValueError('Speed unit must be of %s' % str(MPS))
        self._unit = unit
        self._value = speed

    @property
    def mps(self) -> float:
        """ speed value in `mps` """
        return self._value * MPS['mps']

    @property
    def kmh(self) -> float:
        """ speed value in `kmh` """
        return self._value * MPS['kmh']

    @property
    def mph(self) -> float:
        """ speed value in `mph` """
        return self._value * MPS['mph']

    def __float__(self):
        return self.mps

    def __str__(self):
        return '%0.2f mps (%0.2f km/h)' % (self.mps, self.kmh)

    def __repr__(self):
        return str(self.kmh)

    def __add__(self, other):
        return Speed(float(self).__add__(float(other)))

    def __sub__(self, other):
        return Speed(float(self).__sub__(float(other)))

    def __mul__(self, other):
        return Speed(float(self).__mul__(float(other)))

    def __truediv__(self, other):
        return Speed(float(self).__truediv__(float(other)))

    def __bool__(self):
        return float(self).__bool__()

    def __cmp__(self, other):
        return float(self).__cmp__(float(other))

    def __eq__(self, other):
        return float(self).__eq__(float(other))

    def __hash__(self):
        return hash(float(self))
