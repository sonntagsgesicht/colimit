

**colimit** is a python library to support the
`mathematical project on mobility <https://fbmn.h-da.de/~hoffmann/index.php/Lehre/Projekt>`_
at `Darmstadt University of Applied Sciences <http://mn.h-da.de>`_.

The focus of the project is to provide robust path predictions
based on instantaneous geo-location data.

The later are given as positional gps coordinate
in **latitude** and **longitude** as well as data of motion by **speed** and **direction**.

At first - based on these geo-location data - the project will provide algorithm
to predict which way we are moving on.
Here, *way* is in the sense of
`OpenStreetMap <https://wiki.openstreetmap.org/wiki/way>`_.

And in a second step, list of ways are extracted and
sorted in the descending order being expected to be taken.

All those predictions are under resource restrictions like
limited time, cpu power and data traffic.

As a practical application the algorithm may be supplied
to a `mobile app <https://www.apple.com/de/app-store/>`_ backend.
This is a python server application, which provides *speed limit* information
according the way the mobile user is assumed to be driving on.

Therefore the mobile app provides geo-location data of its current position and motion.
The server backend adds functionality to select ways around those position.
Next the supplied algorithm filters and sorts a requested list of ways.
Finally the sorted list of ways is send back to the mobile device.

Once identified, information about the ways on speed limits are displayed on the mobile app.

Quick Start
-----------

First, install then **colimit** library.
The latest stable version can always be installed or updated via
`pip <https://pip.pypa.io/en/stable/>`_:

.. code-block:: bash

    $ pip install https://limits.pythonanywhere.com/limits.zip

Now, we can start `python <https://python.org>`_ interpreter
and import the project simply by

.. code-block:: python

    >>> import colimit

after installation.

Create a file for your ``get_limit`` function, which is the delegate function
for your algorithm with in the server backend.

This file should implement as fixed signature:

.. code-block:: python

    def get_limit(latitude, longitude, speed, direction, get_ways):
        limit, ways = 1.0, ()
        # ... your code ...
        return limit, ways

For details on the arguments and return value, see |Connection().get_limit()|.
Note all arguments are :class:`float` except **get_ways**.
**get_ways** will be a function, for details see |Connection().get_ways()|.
It can be used to request a list of |Way()| objects within your `get_limit` function.
Now, it is your turn to filter and sort clever!

There are only a few other classes involved, as |Speed| which is just a simple extension
of :class:`float` to provide convenient unit con version
from *km/h* or *mph* to *mps* and back. This is useful since internally all speed
figures are in *mps*.

.. code-block:: python

    >>> # create speed from value in unit 'kmh'
    >>> v = Speed(30, unit='kmh')
    >>> v
    8.33 mps (30.00 km/h)

    >>> # convert back to 'kmh' as a float
    >>> v.kmh
    30.0

    >>> type(v.kmh)
    <class 'float'>

    >>> # convert to 'miles per hour' as a float
    >>> v.mph
    18.64116666666667

    >>> # Speed inductances admit simple operations like + and -
    >>> v + colimit.Speed(1, 'mps')
    9.33 mps (33.60 km/h)

    >>> # and * or / with any float or int
    >>> v * 2
    16.67 mps (60.00 km/h)

Any |Way| is technically given as a ordered set of points
(`nodes <https://wiki.openstreetmap.org/wiki/Node>`_),
which is simply a list of
`gps coordinate <https://en.wikipedia.org/wiki/Geographic_coordinate_system>`_.
Each gps coordinate of **latitude** and **longitude** states a geo-|Location| data
which can be enriched by data of motion **speed** and **direction**.
The later can be used to predict future positions, again expressed as |Location|.

.. code-block:: python

    >>> # a simple location given by gps coordinate
    >>> hda = colimit.Location(latitude=49.867219, longitude=8.638495)
    >>> hda
    Location at (49.867219,08.638495) at 21-08-29:22-46-51

    >>> hda.coordinate
    (49.867219, 8.638495)

    >>> # enriched by data of motion
    >>> speed = colimit.Speed(30, 'kmh').mps
    >>> direction = 41.0  # cardinal direction in degrees to north=0.0
    >>> loc = colimit.Location(latitude=49.867219, longitude=8.638495,
                               speed=speed, direction=direction)
    >>> loc
    Location at (49.867219,08.638495) with speed 30.0 km/h in direction 41.00° at 21-08-29:22-49-32

    >>> # using geometric calculations one predicts the position in future time
    >>> nxt =loc.next(timedelta=2.0)  # position under constant motion in two seconds
    >>> nxt
    Location at (49.867317,08.638608) with speed 30.0 km/h in direction 41.00° at 21-08-29:23-36-12

    >>> # again using geometric calculations one derives the distance between to points
    >>> loc.dist(nxt)  # distance in meter
    16.666666666775978

Since such prediction of motion differ on a sphere or ellipsoid to the motion
in the flat plane, this becomes a geometric problem. By default, |Location| uses
planar geometry. The relevant algorithm are |Location.polar()| and |Location.xy()|
which can be replaced by more elaborated ones if needed.

Moreover, to select the most reasonable way depending on |Location| is a geometric
problem, too. Each way is a polygon with vertices being |Location| points.
So a way edge or way segment is just given by the line between tow |Location| points.
To decide which way segment fits best, distances and directions
in non planar geometry have to be derived.

All this will take place in the ``get_limit`` file using plain python functionality
plus the three **colimit** classes |Speed|, |Location| and |Way|.

Once implemented, the file can be tested locally using |Connection.get_limit()| with
|Connection.get_ways()|. Further test tools like |test()| and |gpx()| may be supportive.

After successful local testing the ``get_limit`` file can be uploaded
using a |Connection.update_get_limit_code()| to the backend server.
Now user tests on mobile devices can follow
to evaluate the performance of the algorithm in practice.


License
-------

Code and documentation are only available for personal usage during the project course.
No re-use without permission by the author (jan-philipp.hoffmann (at) h-da.de).


