# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.9, copyright Monday, 13 September 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__doc__ = 'better know your limits'
__license__ = 'No License - only for h_da staff or students'

__author__ = 'sonntagsgesicht'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://sonntagsgesicht.github.com/' + __name__

__date__ = 'Monday, 13 September 2021'
__version__ = '0.1.9'
__dev_status__ = '2 - Beta'

__dependencies__ = 'requests',
__dependency_links__ = ()
__data__ = "*.zip",
__scripts__ = ()

from .limits import Connection
from .location import Location
from .speed import Speed
from .testing import gpx, test
from .way import Way

__all__ = 'Speed', 'Location', 'Way', 'Connection', 'gpx', 'test'
