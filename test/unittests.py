# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.9, copyright Monday, 13 September 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import os
import sys
import unittest
import logging
import datetime

sys.path.append('..')

pkg = __import__(os.getcwd().split(os.sep)[-1])
from colimit import Speed, Location, Way, Connection, gpx, test
from colimit.testing import _Tester, _import

logging.basicConfig()


class FirstUnitTests(unittest.TestCase):
    def setUp(self):
        path = 'data'
        if not os.path.exists(path):
            path = os.path.join('test', path)

        self.ci = Connection(
            username="colimit_test",
            url="http://macbook-philipp.local",
            port=5000
        )
        if not self.ci.online:
            self.ci = Connection(username="colimit_test")

        self.pub_key = os.path.join(path, "key.pub")

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
            self.locations.append(self.locations[-1].next(id=10 + i))

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

        self.gpx_file_wo_time = os.path.join(path, "rhg_wo_time.gpx")
        self.gpx_file = os.path.join(path, "rhg.gpx")
        self.get_limit_file = os.path.join(path, "colimit_test.py")
        self.file_cache = os.path.join(path, "file_cache")

        if os.path.exists(self.file_cache):
            for filename in os.listdir(self.file_cache):
                full_name = os.path.join(self.file_cache, filename)
                if os.path.exists(full_name) and full_name.endswith('.json.zip'):
                    os.remove(full_name)

    def tearDown(self):
        if os.path.exists(self.file_cache):
            for filename in os.listdir(self.file_cache):
                full_name = os.path.join(self.file_cache, filename)
                if os.path.exists(full_name) and full_name.endswith('.json.zip'):
                    os.remove(full_name)

    def test_pkg_name(self):
        self.assertEqual(os.getcwd().split(os.sep)[-1], pkg.__name__)

    def test_speed(self):
        spd = self.speed
        value = float(self.speed)
        self.assertTrue(isinstance(str(spd), str))
        self.assertTrue(isinstance(repr(spd), str))

        self.assertAlmostEqual(float(Speed(value)), value)
        self.assertAlmostEqual(float(Speed(value, 'kmh')), value / 3.6)
        self.assertAlmostEqual(float(Speed(value, 'kmh')),
                               value / float(Speed(1).kmh))
        self.assertAlmostEqual(float(Speed(value, 'kmh').kmh), value)
        self.assertAlmostEqual(float(Speed(value, 'mph').mph), value)
        self.assertAlmostEqual(float(Speed(value, 'fts').fts), value)
        self.assertAlmostEqual(float(Speed(value, 'knots').knots), value)

    def test_xy(self):
        c, cc = 0, 0
        xy = (1, 1), (1, -1), (-1, -1), (-1, 1)
        for x, y in xy:
            x, y = c + x, cc + y
            r, d = Location.polar(c, cc, x, y)

            a, b = Location.xy(c, cc, r, d)
            self.assertAlmostEqual(x, a)
            self.assertAlmostEqual(y, b)

            s, e = Location.polar(c, cc, a, b)
            self.assertAlmostEqual(r, s)
            self.assertAlmostEqual(d, e)

    def test_location(self):
        loc = self.location
        self.assertTrue(isinstance(str(loc), str))
        self.assertTrue(isinstance(repr(loc), str))

        self.assertAlmostEqual(loc.latitude, self.latitude)
        self.assertAlmostEqual(loc.longitude, self.longitude)
        self.assertAlmostEqual(float(loc.speed), float(self.speed))
        self.assertAlmostEqual(loc.direction, self.direction)

        loc_dict = loc.clone()
        self.assertEqual(loc, loc_dict)

        self.assertEqual(next(loc), loc.next())
        loc_2 = loc.next(radius=30, direction=45)
        loc_3 = loc.diff(loc_2)
        loc_4 = loc_3.next()
        # print(loc, loc_2, loc_3, loc_4, sep='\n')

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

        a = Location(latitude=0.2+loc.latitude, longitude=0.1+loc.longitude,
                     speed=2*loc.speed.mps, direction=2*loc.direction)

        p = loc.project(a)
        self.assertNotEqual(loc, p)
        self.assertEqual(p, p.project(a))

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
        way = Way(id=111, limit=float(self.speed))
        way.geometry = self.locations
        for g in way.geometry:
            self.assertTrue(g in way)

        way_dict = Way(**way._dict)
        self.assertEqual(way, way_dict)
        self.assertTrue(isinstance(str(way), str))
        self.assertTrue(isinstance(repr(way), str))

        way = Way(id=123, limit=float(self.speed), geometry=gpx(self.gpx_file))
        south_west, north_east = way.boundary
        self.assertEqual(Location(49.866743,07.990217), south_west)
        self.assertEqual(Location(50.053581,08.666603), north_east)
        center = way.center
        self.assertEqual(Location(49.960162,08.328410), center)
        dx, dy = way.diameter
        self.assertAlmostEqual(75294.94509969912, dx)
        self.assertAlmostEqual(20798.711020833827, dy)
        length = way.length
        duration = way.duration
        self.assertAlmostEqual(92511.01945196062, length)
        self.assertEqual(datetime.timedelta(seconds=2432), duration)

    def test_testing(self):
        locations = gpx(self.gpx_file_wo_time)
        self.assertEqual(57, len(locations))
        locations = gpx(self.gpx_file)
        self.assertEqual(2299, len(locations))
        t = _Tester()
        test(locations, lambda **x: (Way(),), self.get_limit_file, tester=t)
        self.assertEqual(len(locations), len(t.fails))
        print(t)

    def test_plot(self):
        self.assertTrue(self.ci.online, 'limits server offline')
        self.assertTrue(self.ci.connected, 'not connected to limits server')
        t = _Tester()
        locations = gpx(self.gpx_file)[::200]
        test(locations, self.ci.get_ways, self.get_limit_file, tester=t)
        t.plot(file=self.gpx_file + '.pdf', column='speed', quiver=True)

    def test_limits(self):
        self.assertTrue(self.ci.online, 'limits server offline')
        self.assertTrue(self.ci.connected, 'not connected to limits server')
        get_limit = _import(self.get_limit_file)

        self.ci.update_get_limit_code(self.get_limit_file)
        result = self.ci.get_ways(**self.swne_dict)
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(29, len(result))
        self.assertTrue(all(isinstance(w, Way) for w in result))

        self.assertTrue(os.path.exists(self.file_cache))
        self.assertEqual(0, len(os.listdir(self.file_cache)))
        result = self.ci.get_ways(**self.swne_dict, file_cache=self.file_cache)
        self.assertEqual(1, len(os.listdir(self.file_cache)))
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(29, len(result))
        self.assertTrue(all(isinstance(w, Way) for w in result))

        result = self.ci.get_ways(**self.swne_dict, file_cache=self.file_cache)
        self.assertEqual(1, len(os.listdir(self.file_cache)))
        self.assertTrue(isinstance(result, tuple))
        self.assertEqual(29, len(result))
        self.assertTrue(all(isinstance(w, Way) for w in result))

        limit, ways = get_limit(get_ways=self.ci.get_ways, **self.llsd_dict)
        limit_online, ways_online = self.ci.get_limit(**self.llsd_dict)
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
