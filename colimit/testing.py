# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


from importlib import reload
from datetime import datetime
from os.path import split
import sys

from timeit import default_timer as timer
import xml.etree.ElementTree as XTree

from .location import Location
from .speed import Speed


class Tester(object):

    def __init__(self):
        self.fails = list()
        self.timings_1 = list()
        self.timings_2 = list()
        self.eps = 1.
        self.cnt = 0
        self._tape = list()

    @staticmethod
    def _parse_result(result):
        if isinstance(result, tuple) and len(result)==2:
            return result
        if isinstance(result, (int, float, Speed)):
            return float(result), ()
        return -1., ()

    def __call__(self, location, result_1, result_2, time_1, time_2):
        self._tape.append((location, result_1, result_2, time_1, time_2))
        self.cnt += 1
        self.timings_1.append(time_1)
        self.timings_2.append(time_2)
        limit_1, _ = self._parse_result(result_1)
        limit_2, _ = self._parse_result(result_2)
        if abs(float(limit_1) - float(limit_2)) > self.eps:
            self.fails.append((location, result_1, result_2))

    @property
    def total_timings(self):
        return sum(self.timings_1), sum(self.timings_2)

    def __str__(self):
        args = self.cnt, len(self.fails)
        return 'Tester(tested %d locations with %d fails)' % args


def _call_get_limit(location, get_limit, get_ways, cache, folder):
    kwargs = {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'speed': location.speed,
        'direction': location.direction,
        'get_ways': lambda **kw: get_ways(cache=cache, folder=folder, **kw)
    }
    try:
        result = get_limit(**kwargs)
        return result
    except ZeroDivisionError as e:
        msg = type(e).__name__ + '("' + str(e) + '")'
        print(msg)


def _import(get_limit_file):
    if get_limit_file:
        heads, tail = split(get_limit_file)
        if heads not in sys.path:
            sys.path.append(heads)
        module = __import__(tail.replace('.py', ''),
                            fromlist=('get_limit',))
        module = reload(module)
        return getattr(module, 'get_limit') if module else None


def gpx(gpx_file, wpt=False, geometry=None):
    """
    <gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogr="http://osgeo.org/gdal" xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="GDAL 3.0.4" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
      <metadata>
        <bounds minlat="49.865450455524133" minlon="8.633527001159154" maxlat="49.869904851145897" maxlon="8.639932498881354"/>
      </metadata>
      <wpt lat="49.869597505257772" lon="8.633527001159154">
        <time>2019-12-06T14:19:25Z</time>
      </wpt>
      <trk>
        <name>h_da</name>
        <trkseg>
          <trkpt lat="49.869597505257772" lon="8.633527001159154">
        	<ele>99.07395026675061</ele>
            <time>2019-12-06T14:20:00Z</time>
          </trkpt>
        </trkseg>
      </trk>
    </gpx>
    """
    pre = '{http://www.topografix.com/GPX/1/1}'
    tag = pre + ('wpt' if wpt else 'trkpt')
    time = pre + 'time'
    datetime_format = '%Y-%m-%dT%H:%M:%SZ'

    total_dist = 0.0
    location_list = list()
    last = Location(geometry=geometry)
    root = XTree.parse(gpx_file)
    for child in root.iter(tag):
        lat = float(child.attrib.get('lat', 0.0))
        lon = float(child.attrib.get('lon', 0.0))
        tm = datetime.strptime(child.find(time).text, datetime_format)
        pnt = Location(lat, lon, time=tm, geometry=geometry)
        if last:
            diff = last.diff(pnt)
            if 0. < float(diff.speed):
                dt = diff.timedelta.total_seconds()
                dt = dt if dt else 1.0
                total_dist += float(diff.speed) / dt
                location_list.append(diff)
            else:
                # ignore entries with no movement since the time moves always
                pnt = last
        last = pnt
    if location_list:
        cnt = len(location_list)
        total_dist_kmh = total_dist / 1000.
        duration = last.time - location_list[0].time
        avg_spd = Speed(total_dist / duration.total_seconds())
        print('track found in %s' % gpx_file, end='')
        print(' with %d entries' % cnt, end='')
        print(' and total distance of %0.3f km' % total_dist_kmh, end='')
        print(', duration %s' % str(duration), end='')
        print(' and average speed of %s' % str(avg_spd))
    return location_list


def test(locations, get_ways, get_limit_file, get_limit_file_2=None,
         tester=Tester(), cache=dict(), folder='data'):

    # build testing `get_limit`
    get_limit = _import(get_limit_file)
    get_limit_2 = _import(get_limit_file_2)

    # make actual function call
    for location in locations:
        start = timer()
        result = _call_get_limit(location, get_limit, get_ways, cache, folder)
        step = timer() - start
        result_2 = None
        step_2 = 0.0
        if get_limit_2:
            start_2 = timer()
            result_2 = _call_get_limit(location, get_limit_2, get_ways, cache, folder)
            step_2 = timer() - start_2
        tester(location, result, result_2, step, step_2)
    return tester
