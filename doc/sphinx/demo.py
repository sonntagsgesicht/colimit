# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.9, copyright Monday, 13 September 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


from colimit import Location

EARTH_CIRCUMFERENCE = 40075000.0


def min_dist_to_way_nodes(loc, way):
    if not way.geometry:
        return EARTH_CIRCUMFERENCE
    return min(loc.dist(g) for g in way.geometry)


def get_limit(latitude, longitude, speed, direction, get_ways):
    limit, ways = -1.0, ()
    # note 'get_ways' requires keyword arguments. positional arguments like
    # get_ways(latitude, longitude, 2*speed) are not allowed!
    ways = get_ways(latitude=latitude, longitude=longitude, radius=2 * speed)
    if not ways:
        return limit, ()
    loc = Location(latitude)
    data = list((min_dist_to_way_nodes(loc, way), way) for way in ways)
    data.sort(key=lambda pair: pair[0])  # sort by min_dist_to_way_nodes
    # not the best choice to do but a good starting point
    return ways[0].limit, ways


if __name__ == "__main__":

    import os
    import sys
    from colimit import Connection

    get_limit_file = 'full path to your file'
    # add file location to sys.path to be able to import it as a modul
    path, file = os.path.split(get_limit_file)
    if path not in sys.path:
        sys.path.append(path)
    module = __import__(file.replace('.py', ''))  # , fromlist=(FUNC_NAME,))
    get_limit = getattr(module, 'get_limit')
    # now, 'get_limit' can be tested

    # setup server connection
    user, password = 'your username', 'your password'
    url, port = 'https://limits.pythonanywhere.com', 443

    # start connection to limits server
    ci = Connection(user, password, url, port)

    # add file location to ``sys.path`` to be able to import it as a module
    get_limit_file = 'full path to your file'
    path, file = os.path.split(get_limit_file)
    if path not in sys.path:
        sys.path.append(path)
    module = __import__(file.replace('.py', ''))
    get_limit = getattr(module, 'get_limit')

    # now, 'get_limit' can be tested.
    # But before testing it online test it with real data do it locally.

    # Sometimes it is useful during development to setup up a ``file_cache``
    # file to store result as a json.zip file so it can be re-used next time.

    lat, lon, rad = 49.870210, 8.632949, 20.
    spd, dir, sec = 10., 10., 1.
    file_cache = "%2.6f-%3.6f_%3.2f" %(lat, lon, rad)

    # now invoke 'get_ways' for testing purpose
    # (using file_cache to reduce server traffic)

    ways = ci.get_ways(latitude=lat, longitude=lon, radius=rad,
                       file_cache=file_cache)
    len(ways)

    # And to test the 'get_limit' function use 'ci.get_ways'

    loc = Location(lat, lon, spd, dir, sec)
    limit, sorted_ways = get_limit(location=loc, get_ways=ci.get_ways)
    print(len(ways) == len(sorted_ways))  # check both list are of same length
    print(all(way in sorted_ways for way in ways))

    # In order to test multiple location use |test()|.
    # And use |gpx()| to generate a list of locations from a *gpx file*.
    from colimit import gpx, test
    gpx_file = "da.gpx"
    locations = gpx(gpx_file)
    len(locations)
    10
    test(locations, ci.get_ways, get_limit_file)
    ...

    # To avoid heavy printing, use a tester which is callable.
    # The tester should collect and evaluate the result for each test location.
    from colimit.testing import _Tester
    tester = _Tester
    test(locations, ci.get_ways, get_limit_file, tester=tester)
    print(tester.fails)

    # Now, evaluate the tests and improve the ``get_limit`` code and test again.

    # To test the ``get_limit`` code online, update the online code

    ci.update_get_limit_code(get_limit_file)

    # and check if it works as expected
    kwargs = {'latitude': lat, 'longitude':lon, 'speed': spd, 'direction': dir}
    limit_local, ways_local = get_limit(get_ways=ci.get_ways, **kwargs)
    limit_online, ways_online = ci.get_limit(**kwargs)
    print(limit_local == limit_online)
    print(len(ways_local) == len(ways_online))

    # Now, further practical user tests can take place
    # in the `mobile app <https://www.apple.com/de/app-store/>`_
    # (after setting up our username in app settings).

    # And don't forget: Test only as a passenger.

    # Don't test and drive! Drive responsible, keep always focus on the traffic.
