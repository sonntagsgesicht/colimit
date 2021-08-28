# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__doc__ = 'better know your limits'
__license__ = 'No License - only for h_da staff or students'

__author__ = 'Jan-Philipp Hoffmann'
__email__ = 'jan-philipp.hoffmann@h-da.de'
__url__ = 'https://code.fbi.h-da.de/' + __name__

__date__ = 'Friday, 27 August 2021'
__version__ = '0.1.6'
__dev_status__ = '3 - Alpha'

__dependencies__ = 'requests',
__dependency_links__ = ()
__data__ = "*.zip",
__scripts__ = ()

from .limits import Connection
from .location import Location
from .speed import Speed
from .testing import gpx, test
from .way import Way

__all__ = 'Speed', 'Location', 'Way', 'Connection', \
          'H_DA', 'FFM', 'gpx', 'test'

H_DA = Location(49.867219, 8.638495)
FFM = Location(50.105993, 8.665267, 34.4, 3.32)



'''
Backlog
=======
- doc
- add dev plotting to visualise motion
build release with: `python setup.py sdist --formats=zip`
'''
