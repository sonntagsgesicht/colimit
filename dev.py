# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.8, copyright Tuesday, 31 August 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import os
import logging

pkg = __import__(os.getcwd().split(os.sep)[-1])

logging.basicConfig()

if True:
    from colimit import Connection, gpx, test
    from colimit.testing import _Tester

    user = password = "h_da_test"
    url, port = "http://macbook-philipp.local", 5000
    #url, port = "https://limits.pythonanywhere.com", 443
    get_limit_file = 'test/data/h_da_test.py'
    gpx_file = 'test/data/rhg.gpx'

    locations = gpx(gpx_file)[:111]
    ci = Connection(user, password, url, port)
    t = _Tester()
    test(locations, ci.get_ways, get_limit_file, tester=t)
    t.plot(file=gpx_file + '.pdf', column='speed')

    # df = pd.DataFrame(d)
    # geometry = geopandas.points_from_xy(df.longitude, df.latitude)
    # gdf = geopandas.GeoDataFrame(df, geometry=geometry, crs='WGS-84')
    #
    # ax = gdf.plot(cmap="RdYlGn_r", column='speed', markersize=1, edgecolor="k",
    #               linewidth=5, marker='o',
    #               figsize=(20, 20), legend=True, aspect='equal')
    # cx.add_basemap(ax, crs=gdf.crs.to_string(), source=cx.providers.CartoDB.Voyager)
    # plt.savefig(gpx_file + '.pdf')
    # plt.show()


if False:
    lat = 49.86454025314968
    lon = 8.638326231714982
    get_ways(latitude=lat, longitude=lon, radius=100, file='Darmstadt')

if False:
    from dev.geometry import SphericalGeometry as geometry

    locations = pkg.testing.gpx('data/gpx/rhg.gpx', geometry=geometry)[:100]
    t = pkg.test(locations, 'data/uploads/d7c5621f.py',
                 'data/uploads/e74ddd33.py')
    print(t)

if False:
    from datetime import datetime
    import xml.etree.ElementTree as XTree

    gpx = """
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
    trkpt = pre + 'trkpt'
    wpt = pre + 'wpt'
    time = pre + 'time'
    datetime_format = '%Y-%m-%dT%H:%M:%SZ'
    root = XTree.fromstring(gpx)
    for child in root.iter(wpt):
        lat = float(child.attrib.get('lat', 0.0))
        lon = float(child.attrib.get('lon', 0.0))
        tm = datetime.strptime(child.find(time).text, datetime_format)
        print(lat, lon, tm)

if False:
    from datetime import datetime as dt, timedelta as td

    eps = 1e-7
    shift = 20
    t, b = 1., pkg.Location(50, 8, 30, 45, dt.now() - td(seconds=shift))
    a, c = pkg.location.boundary(b, 100, 50)
    # assert a.latitude == b.latitude + degrees(dy / E_CONST)
    # assert self.longitude == other.latitude + degrees(dx / E_CONST) / c
    print(b.dist())
    print(c.dx_dy(b))
    print(c.dist(a))
    print(b)
    print(b.diff(c))
    print(b.diff(c).in_sec(shift))
    print(c)
    print(c + td(seconds=10))
    d = b.diff(c)
    print(b.dist(d), b + d)
    print(c.dist(next(d)))

if False:
    response = json.load(open('response.json', 'r'))
    ways = pkg.way.get_ways_from_oms_elements(response['elements'])
    for w in ways:
        print(w._dict)

if False:
    # print('out:', len(pkg.call_cache(area='Messel')))
    print('out:', len(pkg.get_ways(area='Messel')))
    print('out:', len(pkg.get_ways()))
    print('out:',
          len(pkg.get_ways(south=49.9, west=7.99, north=50.0, east=8.0)))
    print('out:', len(pkg.get_ways(file='Darmstadt_partial',
                                   location=pkg.H_DA, radius=200, force=True)))
    print('out:', len(pkg.get_ways(file='Darmstadt_partial',
                                   location=pkg.H_DA, radius=50)))

if False:
    # area[name = "Hessen"]; out;
    location = pkg.Location(50.0, 8.0)
    ways = pkg.get_ways(area='Hessen', file='data/json/Hessen.json.zip',
                        timeout=360)
    for w in ways:
        if location in w:
            print(w.boundary)

if False:
    from itertools import chain

    ab = itertools.chain(['it'], ['was'], ['annoying'])
    list(ab)
    # pkg.get_ways(latitude=50.0, longitude=8.0, radius=75.0)
    # pkg.get_ways(south=49.9995, west=7.999, north=50.0005, east=8.001)
    for city in 'Darmstadt', 'Bonn', 'Mainz', 'Wiesbaden', 'Heidelberg', \
                'Messel', 'Griesheim', 'Trebur', \
                'Geisenheim', 'Oestrich-Winkel':
        file = './colimit/data/' + city + '.json'
        ways = pkg.get_ways(area=city, timeout=180, file=file)
        b = Way(geometry=chain(*tuple(w.geometry for w in ways))).boundary
        print('boundary:', b)

if False:
    response = pkg.call_overpass(49.9995, 7.999, 100.0)
    response = pkg.call_overpass(south=49.9995, west=7.999,
                                 north=50.0005, east=8.001,
                                 timeout=60)
    with open('response.json', 'w') as f:
        f.write(dumps(response))

    with open('response.json', 'r') as f:
        response = loads(f.read())

    ways = pkg.get_ways_from(response['elements'])
    for w in ways:
        print(w.boundary)
    print(len(ways), 'ways')
