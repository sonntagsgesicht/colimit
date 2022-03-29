# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.12, copyright Tuesday, 29 March 2022
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__doc__ = 'better know your limits'
__license__ = 'No License - only for h_da staff or students'

__author__ = 'sonntagsgesicht'
__email__ = 'sonntagsgesicht@icloud.com'
__url__ = 'https://sonntagsgesicht.github.com/' + __name__

__date__ = 'Tuesday, 29 March 2022'
__version__ = '0.1.12'
__dev_status__ = '4 - Beta'

__dependencies__ = 'requests', 'pandas', 'geopandas', 'contextily', \
    'matplotlib', 'bs4'
__dependency_links__ = ()
__data__ = "*.zip", "*.gpx"
__scripts__ = ()
__theme__ = 'sphinx_rtd_theme'


from .limits import Connection  # noqa E402
from .location import Location  # noqa E402
from .speed import Speed  # noqa E402
from .testing import gpx, test  # noqa E402
from .way import Way  # noqa E402

__all__ = 'Speed', 'Location', 'Way', 'Connection', 'gpx', 'test'
