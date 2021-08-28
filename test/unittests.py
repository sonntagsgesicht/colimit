# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import os
import sys
import unittest
import logging
import datetime

sys.path.append('..')

pkg = __import__(os.getcwd().split(os.sep)[-1])
from colimit import Speed, Location, Way, Connection, gpx, test

logging.basicConfig()


class FirstUnitTests(unittest.TestCase):
    def setUp(self):
        self.user = self.password = "h_da_test"
        self.url, self.port = "http://macbook-philipp.local", 5000
        # self.url, self.port = "https://limits.pythonanywhere.com", 80
        self.pub_key = "data/key.pub"

        self.radius = 123.4
        self.latitude, self.longitude = 49.867219, 8.638495
        self.speed = Speed(23.23)
        self.direction = 69.1
        self.one_sec = datetime.timedelta(seconds=1.234)

        self.location = Location(self.latitude, self.longitude,
                                 self.speed, self.direction,
                                 timedelta=self.one_sec)
        self.locations = [self.location]
        for i in range(10):
            self.locations.append(self.locations[-1].next(next_id=10 + i))

        sw, ne = Location.boundary(*self.locations, radius=self.radius)
        self.swne_dict = {
            'south': sw.latitude, 'west': sw.longitude,
            'north': ne.latitude, 'east': ne.longitude,
        }
        self.llr_dict = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
        }
        self.llsd_dict = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'direction': self.direction
        }

        self.gpx_file = 'data/gpx/rhg.gpx'
        self.get_limit_file = 'data/uploads/h_da_test.py'

    def test_pkg_name(self):
        self.assertEqual(os.getcwd().split(os.sep)[-1], pkg.__name__)

    def test_speed(self):
        value = float(self.speed)
        self.assertAlmostEqual(float(Speed(value)), value)
        self.assertAlmostEqual(float(Speed(value, 'kmh')), value / 3.6)
        self.assertAlmostEqual(float(Speed(value, 'kmh')),
                               value / float(Speed(1).kmh))
        self.assertAlmostEqual(float(Speed(value, 'kmh').kmh), value)

    def test_location(self):
        loc = self.location
        self.assertAlmostEqual(loc.latitude, self.latitude)
        self.assertAlmostEqual(loc.longitude, self.longitude)
        self.assertAlmostEqual(float(loc.speed), float(self.speed))
        self.assertAlmostEqual(loc.direction, self.direction)

        loc_dict = Location(**loc.dict)
        self.assertEqual(loc, loc_dict)

        self.assertEqual(next(loc), loc.next())
        loc_2 = loc.next(radius=30, direction=45)
        loc_3 = loc.diff(loc_2)
        loc_4 = loc_3.next()
        print(loc, loc_2, loc_3, loc_4, sep='\n')

        self.assertAlmostEqual(30., loc.dist(loc_2))
        self.assertAlmostEqual(0.0, loc_2.dist(loc_4))

        self.assertAlmostEqual(loc.latitude, loc_3.latitude)
        self.assertAlmostEqual(loc_2.latitude, loc_4.latitude)

        self.assertAlmostEqual(loc.longitude, loc_3.longitude)
        self.assertAlmostEqual(loc_2.longitude, loc_4.longitude)

        self.assertAlmostEqual(loc.speed, loc_2.speed)
        self.assertAlmostEqual(loc_3.speed, loc_4.speed)

        self.assertAlmostEqual(loc.direction, loc_2.direction)
        self.assertAlmostEqual(loc_3.direction, loc_4.direction)

        self.assertAlmostEqual(loc.time + self.one_sec, loc_2.time)
        self.assertAlmostEqual(loc_3.time + self.one_sec, loc_4.time)

        self.assertAlmostEqual(loc.timedelta, loc_2.timedelta)
        self.assertAlmostEqual(loc_3.timedelta, loc_4.timedelta)

    def test_boundary(self):
        radius = 123.45
        inner_left, inner_right = Location.boundary(*self.locations)
        outer_left, outer_right = Location.boundary(*self.locations,
                                                    radius=radius)
        self.assertAlmostEqual(self.locations[0].latitude, inner_left.latitude)
        self.assertAlmostEqual(self.locations[0].longitude,
                               inner_left.longitude)
        self.assertAlmostEqual(self.locations[-1].latitude,
                               inner_right.latitude)
        self.assertAlmostEqual(self.locations[-1].longitude,
                               inner_right.longitude)

        other_left, other_right = Location.boundary(inner_right, inner_left,
                                                    radius=radius)
        self.assertEqual(outer_left, other_left)
        self.assertEqual(outer_right, other_right)

        other_left, other_right = Location.boundary(inner_right, radius=radius)
        self.assertEqual(outer_right, other_right)
        other_left, other_right = Location.boundary(inner_left, radius=radius)
        self.assertEqual(outer_left, other_left)

    def test_ways(self):
        way = Way(111, limit=Speed(self.speed))
        way.geometry = self.locations
        for g in way.geometry:
            self.assertTrue(g in way)

        way_dict = Way(**way.dict)
        self.assertEqual(way, way_dict)

    def test_testing(self):
        locations = gpx(self.gpx_file)
        self.assertEqual(2299, len(locations))
        t = test(locations, lambda **x: (Way(),), self.get_limit_file)
        self.assertEqual(len(locations), len(t.fails))
        print(t)

    def test_limits(self):
        path, file = os.path.split(self.get_limit_file)
        if path not in sys.path:
            sys.path.append(path)
        module = __import__(file.replace('.py', ''))# , fromlist=(FUNC_NAME,))
        get_limit = getattr(module, 'get_limit')

        ci = Connection(self.user, self.password, self.url, self.port,
                        verify=self.pub_key)
        ci.update_get_limit_code(self.get_limit_file)

        result = ci.get_ways(**self.swne_dict)
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(28, len(result))
        self.assertTrue(all(isinstance(w, Way) for w in result))

        limit, ways = get_limit(get_ways=ci.get_ways, **self.llsd_dict)
        limit_online, ways_online = ci.get_limit(**self.llsd_dict)
        self.assertAlmostEqual(limit, limit_online)
        self.assertTupleEqual(ways, ways_online)


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print('')
    print('===================================================================')
    print('')
    print(('run %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print('')
    print('-------------------------------------------------------------------')
    print('')

    unittest.main(verbosity=2)

    print('')
    print('===================================================================')
    print('')
    print(('ran %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print(('finished at %s' % str(datetime.datetime.now())))
    print('')
    print('-------------------------------------------------------------------')
    print('')
