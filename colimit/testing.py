# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.8, copyright Tuesday, 31 August 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


from importlib import reload
from datetime import datetime
import os
import sys

from timeit import default_timer as timer
import xml.etree.ElementTree as XTree

from .location import Location
from .speed import Speed


class _Tester(object):

    def __init__(self):
        self.fails = list()
        self.timings_1 = list()
        self.timings_2 = list()
        self.eps = 1.
        self.cnt = 0
        self._tape = list()

    @staticmethod
    def _parse_result(result):
        if isinstance(result, tuple) and len(result) == 2:
            return result
        if isinstance(result, (int, float, Speed)):
            return float(result), ()
        return -1., ()

    def __call__(self, location, result_1, result_2, time_1, time_2):
        """ add test data

        :param location: current test |Location()|
        :param result_1: result of first `get_limit` function
        :param result_2: result of second `get_limit` function or **None**
        :param time_1: execution time of first `get_limit` function
        :param time_2: execution time of second `get_limit` function or 0.0
        """
        self.cnt += 1
        if self.cnt % 80:
            print('.', end="")
        else:
            print('.')
        self._tape.append((location, result_1, result_2, time_1, time_2))
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

    @property
    def geodataframe(self):
        try:
            from pandas import DataFrame
            from geopandas import points_from_xy, GeoDataFrame
        except ImportError:
            print("GeoDataFrame requires the geopandas package.")
            return None
        records = list()
        for loc, r1, r2, t1, t2 in self._tape:
            d = loc.json
            d['timing_1'] = t1
            if isinstance(r1, tuple):
                d['limit_1'], d['ways_1'] = r1
            else:
                d['limit_1'] = r1
            if r2 is not None:
                if isinstance(r2, tuple):
                    d['limit_2'], d['ways_2'] = r2
                else:
                    d['limit_2'] = float(r2)
                d['timing_2'] = t2
                d['limit_diff'] = d['limit_1'] - d['limit_2']
                d['timing_diff'] = d['timing_1'] - d['timing_2']
            records.append(d)
        if records:
            df = DataFrame.from_records(records)
            geometry = points_from_xy(df.longitude, df.latitude)
            return GeoDataFrame(df, geometry=geometry, crs='WGS-84')

    def plot(self, **kwargs):
        try:
            import contextily as cx
            import matplotlib.pyplot as plt
            import matplotlib as mpl
        except ImportError:
            print("Plotting requires the contextily and matplotlib package.")
            return None
        cm = 1 / 2.54
        A4 = 29.7 * cm, 21 * cm

        gdf = self.geodataframe
        if 'limit_diff' in gdf:
            column = 'limit_diff'
            cmap, vmin, vmax = "jet", -50, 50
        else:
            column = 'limit_1'
            cmap, vmin, vmax = "RdYlGn_r", 0, 130

        file = kwargs.pop('file', None)

        kwargs['column'] = kwargs.get('column', column)
        kwargs['cmap'] = kwargs.get('cmap', cmap)
        kwargs['vmin'] = kwargs.get('vmin', vmin)
        kwargs['vmax'] = kwargs.get('vmax', vmax)
        kwargs['figsize'] = kwargs.get('figsize', A4)
        kwargs['aspect'] = kwargs.get('aspect', 'equal')

        # ax = gdf.plot(cmap="RdYlGn_r", column='speed', vmin=0, vmax=130,
        #               markersize=5, marker='o', figsize=A4, aspect='equal')

        ax = gdf.plot(**kwargs, legend=True, legend_kwds={'orientation':'horizontal'})
        cx.add_basemap(ax, crs=gdf.crs.to_string(),
                       source=cx.providers.CartoDB.Voyager)
        ax.set_title(column)
        if file is not None:
            print("save plot to", file)
            plt.savefig(file, bbox_inches="tight")
        plt.show()


def _call_get_limit(location, get_limit, get_ways, cache=None, folder=''):
    kwargs = {
        'latitude': location.latitude,
        'longitude': location.longitude,
        'speed': location.speed,
        'direction': location.direction,
        'get_ways': get_ways
        # 'get_ways': lambda **kw: get_ways(cache=cache, folder=folder, **kw)
    }
    try:
        result = get_limit(**kwargs)
        return result
    except ZeroDivisionError as e:
        msg = type(e).__name__ + '("' + str(e) + '")'
        print(msg)


def _import(get_limit_file):
    if get_limit_file:
        if isinstance(get_limit_file, (str, bytes, int, os.PathLike)):
            if not os.path.exists(get_limit_file):
                return None
            heads, tail = os.path.split(get_limit_file)
            if heads not in sys.path:
                sys.path.append(heads)
            module = __import__(tail.replace('.py', ''),
                                fromlist=('get_limit',))
            module = reload(module)
            return getattr(module, 'get_limit') if module else None
        else:
            return get_limit_file  # assuming to be get_limit_func


def gpx(gpx_file, wpt=False):
    """ builds list of locations from gpx file

    :param gpx_file: full path to gpx file
        (see https://en.wikipedia.org/wiki/GPS_Exchange_Format)
    :param wpt: bool, if **True** the **wpt** tag entries are used
        to build |Location()| instances in stead of the **trkpt** tag.
        Default is **False**.

    :return: :class:`tuple` (|Location()|)

    """
    """
    <gpx
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:ogr="http://osgeo.org/gdal"
        xmlns="http://www.topografix.com/GPX/1/1"
        version="1.1"
        creator="GDAL 3.0.4"
        xsi:schemaLocation="http://www.topografix.com/GPX/1/1
        http://www.topografix.com/GPX/1/1/gpx.xsd">
      <metadata>
        <bounds
            minlat="49.865450455524133"
            minlon="8.633527001159154"
            maxlat="49.869904851145897"
            maxlon="8.639932498881354"/>
      </metadata>
      <wpt
        lat="49.869597505257772"
        lon="8.633527001159154">
        <time>2019-12-06T14:19:25Z</time>
      </wpt>
      <trk>
        <name>h_da</name>
        <trkseg>
          <trkpt
            lat="49.869597505257772"
            lon="8.633527001159154">
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

    location_list = list()
    last = Location()
    root = XTree.parse(gpx_file)
    for child in root.iter(tag):
        lat = float(child.attrib.get('lat', 0.0))
        lon = float(child.attrib.get('lon', 0.0))
        tm = datetime.strptime(child.find(time).text, datetime_format)
        pnt = Location(lat, lon, time=tm)
        if last:
            diff = last.diff(pnt)
            if 0. < float(diff.speed):
                location_list.append(diff)
            else:
                # ignore entries with no movement since the time moves always
                pnt = last
        last = pnt
    if location_list:
        cnt = len(location_list)
        total_dist = sum(s.dist(s.next()) for s in location_list)
        total_dist_kmh = total_dist / 1000.
        duration = last.time - location_list[0].time
        avg_spd = Speed(total_dist / duration.total_seconds())
        print('track found in %s' % gpx_file, end='')
        print(' with %d %s' % (cnt, ('way' if wpt else 'track') + 'points'))
        print(' starting at %s' % str(location_list[0]))
        print(' ending with %s' % str(location_list[-1]))
        print(' and total distance of %0.3f km' % total_dist_kmh, end=',')
        print(' duration %s' % str(duration), end='')
        print(' and average speed of %s' % str(avg_spd))
    return location_list


def test(locations, get_ways, get_limit_file, get_limit_file_2=None,
         tester=None, cache=dict(), folder='data'):
    """ test function to test or compare `get_limit` codes

    :param locations: list of locations
    :param get_ways: `get_ways` function forwarded
        to get_limit functions as argument
    :param get_limit_file: file to first `get_limit` implementation,
        i.e. function with signature

            `get_limit(latitude, longitude, speed, direction, get_ways)`

        returning the limit and optional a tuple of Ways like
        |Connection().get_limit()|.

    :param get_limit_file_2: second `get_limit` implementation
        to compare first with (optional)
    :param tester: function (optional with default :func:`print()`)
        or callable with signature

            `tester(location, result, result_2, timing, timing_2)`

        where

            * **location** is the |Location|
            * **result** is the return value of first `get_limit`
            * **result_2** is the return value of second `get_limit` or **None**
            * **timing** is the execution time of first `get_limit`
            * **timing_2** is the execution time of second `get_limit` or 0.0

    """
    if tester is None:
        tester = (lambda *x: print(*x))

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
            result_2 = _call_get_limit(location, get_limit_2, get_ways, cache,
                                       folder)
            step_2 = timer() - start_2
        tester(location, result, result_2, step, step_2)
    print()
    return tester
