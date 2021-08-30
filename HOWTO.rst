
First get familiar with the notion of |Speed|, |Location|, |Way|
and the concepts of `nodes <https://wiki.openstreetmap.org/wiki/Node>`_
and `ways <https://wiki.openstreetmap.org/wiki/way>`_.

Note that `nodes <https://wiki.openstreetmap.org/wiki/Node>`_
defining the segments of a `way <https://wiki.openstreetmap.org/wiki/way>`_
as a `polygon <https://en.wikipedia.org/wiki/Polygon>`_
are stored as a sequence of |Location| in |Way().geometry|.

Next create a ``get_limit`` file and - for example - add the following code to it.

.. code-block:: python

    from colimit import Location

    EARTH_CIRCUMFERENCE = 40075000.0


    def min_dist_to_way_nodes(loc, way):
        if not way.geometry:
            return EARTH_CIRCUMFERENCE
        return min(loc.dict(g) for g in way.geometry)


    def get_limit(latitude, longitude, speed, direction, get_ways):
        limit, ways = -1.0, ()
        # note 'get_ways' requires keyword arguments. positional arguments like
        # get_ways(latitude, longitude, 2*speed) are not allowed!
        ways = get_ways(latitude=latitude, longitude=longitude, radius=2*speed)
        if not ways:
            return limit, ()
        loc = Location(latitude)
        data = tuple((min_dist_to_way_nodes(loc, way), way) for way in ways)
        data.sort(key=lambda pair: pair[0])  # sort by min_dist_to_way_nodes
        # not the best choice to do but a good starting point
        return ways[0].limit, ways

Save the file and test it using |Connection()|.

To do so, setup |Connection()|

.. code-block:: python

    import os
    import sys
    from colimit import Connection

    >>> user, password = 'your username', 'your password'
    >>> url, port = 'https://limits.pythonanywhere.com', 443

    >>> # start connection to limits server
    >>> ci = Connection(user, password, url, port)

add file location to ``sys.path`` to be able to import it as a module

.. code-block:: python

    >>> get_limit_file = 'full path to your file'
    >>> path, file = os.path.split(get_limit_file)
    >>> if path not in sys.path:
    >>>     sys.path.append(path)
    >>> module = __import__(file.replace('.py', ''))
    >>> get_limit = getattr(module, 'get_limit')

now, 'get_limit' can be tested.
But before testing it online test it with real data do it locally.

Sometimes it is useful during development to setup up a ``file_cache`` file
to store result as a json.zip file so it can be re-used next time.

.. code-block:: python

    >>> fc = lambda lat, lon, spd
    >>> lat, lon, rad = 49.870210, 8.632949, 20.
    >>> spd, dir, sec = 10., 10., 1.
    >>> file_cache = "data"

now invoke 'get_ways' for testing purpose (using file_cache to reduce server traffic)

.. code-block:: python

    >>>ways = ci.get_ways(latitude=lat, longitude=lon, radius=rad,
                          file_cache=file_cache)
    >>> len(ways)

And to test the 'get_limit' function use 'ci.get_ways'

.. code-block:: python

    >>> loc = Location(lat, lon, spd, dir, sec)
    >>> limit, sorted_ways = get_limit(location=loc, get_ways=ci.get_ways)
    >>> len(ways) == len(sorted_ways)  # check both list are of same length
    True
    >>> all(way in sorted_ways for way in ways)
    True

In order to test multiple location use |test()|.
And use |gpx()| to generate a list of locations from a *gpx file*.

.. code-block:: python

    >>> from colimit import gpx, test
    >>> gpx_file = "da.gpx"

    >>> locations = gpx(gpx_file)
    >>> len(locations)
    10
    >>> test(locations, ci.get_ways, get_limit_file)
    ...

To avoid heavy printing, use a tester which is callable.
The tester should collect and evaluate the result for each test location.

.. code-block:: python

    >>> from colimit.testing import _Tester
    >>> tester = _Tester
    >>> test(locations, ci.get_ways, get_limit_file, tester=tester)
    print(tester.fails)

Now, evaluate the tests and improve the ``get_limit`` code and test again..

To test the ``get_limit`` code online, update the online code

.. code-block:: python

    >>> ci.update_get_limit_code(get_limit_file)

and check if it works as expected

.. code-block:: python

    >>> kwargs = {'latitude': lat, 'longitude':lon, 'speed': spd, 'direction': dir}
    >>> limit_local, ways_local = get_limit(get_ways=ci.get_ways, **kwargs)
    >>> limit_online, ways_online = ci.get_limit(**kwargs)
    >>> limit_local == limit_online
    True
    >>> len(ways_local) == len(ways_online)
    True

Now, further practical user tests can take place
in the `mobile app <https://www.apple.com/app-store/>`_
(after setting up our username in app settings).

.. warning::
    And don't forget: Test only as a passenger.

    Don't test and drive! Drive responsible, keep always focus on the traffic.
