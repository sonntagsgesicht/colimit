# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.12, copyright Monday, 28 March 2022
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import json
import gzip
import os

import requests

from .way import Way

__all__ = "Connection",

URL = "https://limits.pythonanywhere.com"
PORT = "443"
TIMEOUT = 180


class LimitsServerError(Exception):
    """Error on limits server"""
    pass


class Connection(object):

    def __init__(self, username=None, password=None,
                 url=URL, port=None, timeout=None):
        """ |Connection| to a `limits` development server

        :param username: the username
        :param password: the password
        :param url: url to the `limits` server
        :param port: port to connect to server
        :param timeout: timeout for requests

        the `limits` development server stores
        and uses the `get_limit` functions on user requests.

        You can invoke our `get_limit` code online by calling

            `https://<url>:<port>/call/<username>?lat=50.89&lon=8.12&spd=8.4&dir=41.34`

        On instantiation |Connection()| connects to the server.

        It downloads current `get_limit` code on the server
        which then can be retrieved at |Connection().get_limit_code|.

        To update your `get_limit` code
        use |Connection().update_get_limit_code()|.

        To call the `limits` database of geo data you can use
        |Connection().get_ways()|.
        It selects |Way()| items in a requested boundary as it can be done
        within you `get_limit` code.
        It can be used to test your code locally.

        To invoke our `get_limit` code online programmatically use
        |Connection().get_limit()|.

        """

        self._usr = username
        self._pwd = password or username
        self._url = url or URL
        self._port = port or PORT
        self._tmt = timeout
        print('connect as "%s" to %s:%s' % (username, url, port))
        self._key = True

    @property
    def online(self):
        return self._ping()

    @property
    def connected(self):
        return self._ping(auth=True)

    @property
    def _auth(self):
        return self._usr, self._pwd

    @property
    def get_limit_code(self):
        """ current `get_limit` on server side """
        return str(self._download())

    # -- public methods ---

    def update_get_limit_code(self, path=None):
        """ upload `get_limit` code on server side

        :param path: full path to the `get_limit` file

        """
        if os.path.exists(str(path)):
            if not self._upload_from_file(path):
                raise AssertionError("Code update failed.")
            if not self._validate_with_file(path):
                raise AssertionError("Code validation failed.")
        elif path:
            if not self._upload_from_file(file=path):
                raise AssertionError("Code update failed.")
        else:
            if not self._download_to_file(path):
                raise AssertionError("Code download failed.")
        return self.get_limit_code

    def get_limit(self, latitude=None, longitude=None,
                  speed=None, direction=None, location=None, **kwargs):
        """ invoke `get_limit` code online

        :param latitude: latitude in degrees
        :param longitude: longitutde in degrees
        :param speed: speed in mps
        :param direction: direction in degrees north
        :param location: (alternative) |Location()| to retrieve
              **latitude**, **longitude**, **speed** and **direction**
              from. If given, the other arguments may overrule
              the **location** properties.
        :return: :class:`float` as the relevant speed limit or
            (:class:`float`, :class:`tuple` (|Way()|))
            as the relevant speed limit in first place
            and in second place a tuple of |Way()|
            in descending order expected to be taken.

        """
        if location:
            latitude = latitude or location.latitude
            longitude = longitude or location.longitude
            speed = speed or location.speed
            direction = direction or location.direction
        kwargs = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "speed": float(speed),
            "direction": float(direction)
        }
        response = requests.post(
            url=self._build_url('get_limit'),
            auth=self._auth,
            json=kwargs,
            timeout=self._tmt)
        if not response.status_code == 200:
            print(response.status_code, response.reason, response.text)
            raise LimitsServerError(response.text)
        result = response.json()
        limit = result.get('limit', None)
        ways = tuple(Way(**w) for w in result.get('ways', ()))
        return limit, ways

    def get_ways(self, latitude=None, longitude=None, radius=None,
                 south=None, west=None, north=None, east=None, area=None,
                 timeout=None, file_cache=''):
        """ call the `limits` database as inside the `get_limits` code

        :param latitude: in degrees
        :param longitude: in degrees
        :param radius: in meters
        :param south: in degrees
        :param west: in degrees
        :param north: in degrees
        :param east: in degrees
        :param area: string (see https://wiki.openstreetmap.org/wiki/Area)
        :param timeout: timeout seconds in OSM query
        :param file_cache: path to local folder to use or cache request results
            (ignored in online usage on server side)
            Data will be downloaded from the server
            and stored in the **file_cache** folder
            with a standardized file name (with '.json.zip' extension)
            Next time 'get_ways' is invoked with the same arguments
            the file exits and its contents will be returned.
            In this case no data will be downloaded from the server
            until the **file_cache** is removed.

        :return: :class:`tuple` (|Way()|)

        If given
        **latitude**, **longitude** and **radius**
        are used to derive
        **south**, **west**, **north** and **east**
        as the boundary corners in which the selected
        |Way()| objects may be found.

        If **south**, **west**, **north** and **east** are given
        **latitude**, **longitude** and **radius** will be ignored.

        If **area** is given, the resulting data might be filtered by the
        boundary **south**, **west**, **north** and **east** if given.

        """
        timeout = TIMEOUT if timeout is None else timeout
        kwargs = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "south": south,
            "west": west,
            "north": north,
            "east": east,
            "area": area,
            "timeout": timeout,
        }

        if file_cache:
            parts = list()
            if area:
                parts += "area", "%s_" % area
            if all((south, west, north, east)):
                parts += "swen", "lat%08.5f" % south, "lon%08.5f" % west, \
                         "lat%08.5f" % north, "lon%08.5f" % east
            if all((latitude, longitude, radius)):
                parts += "llr", "lat%08.5f" % latitude, \
                         "lon%08.5f" % longitude, "rad%06.2f" % radius
            file_name = "_".join(parts)
            file_name = file_name.replace('.', '-') + ".json.zip"
            file_path = os.path.join(file_cache, file_name)

            if os.path.exists(file_path):
                ways = json.load(gzip.open(file_path, "rt"))
                return tuple(Way(**w) for w in ways)

        response = requests.post(
            url=self._build_url('get_ways'),
            auth=self._auth,
            json=kwargs,
            timeout=self._tmt)
        if not response.status_code == 200:
            print(response.status_code, response.reason, response.text)
            raise LimitsServerError(response.text)
        result = response.json()
        ways = tuple(result['ways'])

        if file_cache:
            json.dump(ways, gzip.open(file_path, 'wt'), indent=2)

        ways = tuple(Way(**w) for w in result['ways'])
        return ways

    # --- private methods ---

    def _build_url(self, mth):
        return self._url + ':' + str(self._port) + '/' + mth

    def _ping(self, auth=False):
        try:
            if auth:
                response = requests.get(
                    url=self._url + ':' + str(self._port),
                    auth=self._auth,
                    verify=self._key)
            else:
                response = requests.get(
                    url=self._url + ':' + str(self._port))
        except requests.exceptions.ConnectionError as e:
            print(e)
            return False
        return response.status_code == 200

    def _download(self):
        response = requests.get(
            url=self._build_url('download'),
            auth=self._auth,
            timeout=self._tmt,
            verify=self._key)
        if not response.status_code == 200:
            print('download of `get_limit` code failed')
            print(response.status_code, response.reason, response.text)
            raise LimitsServerError(response.text)
        print('downloaded `get_limit` code')
        return response.text

    def _upload_from_file(self, path='string', file=None):
        if file:
            response = requests.post(
                url=self._build_url('upload'),
                auth=self._auth,
                files={"filename.py": file},
                timeout=self._tmt,
                verify=self._key)
        else:
            with open(path, "r") as file:
                response = requests.post(
                    url=self._build_url('upload'),
                    auth=self._auth,
                    files={"filename": file},
                    timeout=self._tmt,
                    verify=self._key)
        if not response.status_code == 200:
            print('uploaded `get_limit` code from %s failed' % path)
            print(response.status_code, response.reason, response.text)
            raise LimitsServerError(response.text)
        print('read and uploaded `get_limit` code from %s' % path)
        return True

    def _download_to_file(self, path=""):
        code = self._download()
        if code:
            filepath, _ = os.path.split(path)
            os.makedirs(filepath)
            file = open(path, "r")
            file.write(code)
            file.close()
            print('written `get_limit` code to %s' % path)
            return True
        return False

    def _validate_with_file(self, path):
        code = self._download()
        if code and os.path.exists(path):
            file = open(path, "r")
            file_code = file.read()
            file.close()
            if file_code == code:
                print('validated `get_limit` code with %s' % path)
                return True
            print('failed validation of `get_limit` code with %s' % path)
        return False
