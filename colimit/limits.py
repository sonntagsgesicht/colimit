# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   sonntagsgesicht
# Version:  0.1.7, copyright Sunday, 29 August 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import json
import gzip
import os

import requests

from .way import Way

__all__ = "Connection",

URL = "http://limits.pythonanywhere.com"
PORT = "80"
TIMEOUT = 180
METHODS_WITH_SECRET = 'upload', 'download'


class Connection(object):

    def __init__(self, username, password,
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
        use |Connection.update_get_limit_code()|.

        To call the `limits` database of geo data you can use
        |Connection().get_ways()|.
        It selects |Way()| items in a requested boundary as it can be done
        within you `get_limit` code.
        It can be used to test your code locally.

        To invoke our `get_limit` code online programmatically use
        |Connection().get_limit()|.

        """

        self._usr = username
        self._pwd = password
        self._url = url or URL
        self._port = port or PORT
        self._tmt = timeout
        print('connect as "%s" to %s:%s' % (username, url, port))
        self._key = True
        if not self._ping():
            print('%s:%s is offline' % (url, port))

    @property
    def get_limit_code(self):
        """ current `get_limit` on server side """
        return str(self._download())

    # -- public methods ---

    def update_get_limit_code(self, path):
        """ upload `get_limit` code on server side

        :param path: full path to the `get_limit` file

        """
        if os.path.exists(path):
            if not self._upload_from_file(path):
                raise AssertionError("Code update failed.")
            if not self._validate_with_file(path):
                raise AssertionError("Code validation failed.")
        else:
            if not self._download_to_file(path):
                raise AssertionError("Code download failed.")
        return self.get_limit_code

    def get_limit(self, latitude=None, longitude=None,
                  speed=None, direction=None, location=None):
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
            json=kwargs,
            timeout=self._tmt)
        if not response.status_code == 200:
            raise ConnectionError(response.text)
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
        :param file_cache: path to local file to use or cache request results
            (ignored in online usage on server side)
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

        if file_cache and not file_cache.endswith('.json.zip'):
            file_cache += '.json.zip'

        if os.path.exists(file_cache):
            ways = json.load(gzip.open(file_cache, "rt"))
            return tuple(Way(**w) for w in ways)

        response = requests.post(
            url=self._build_url('get_ways'),
            json=kwargs,
            timeout=self._tmt)
        if not response.status_code == 200:
            raise ConnectionError(response.text)
        result = response.json()
        ways = tuple(result['ways'])
        if file_cache:
            json.dump(ways, gzip.open(file_cache, 'wt'), indent=2)
        ways = tuple(Way(**w) for w in result['ways'])
        return ways

    # --- private methods ---

    def _build_url(self, mth):
        url = self._url + ':' + str(self._port)
        args = url, mth, self._usr
        if mth in METHODS_WITH_SECRET:
            args += self._pwd,
        return "/".join(args)

    def _ping(self):
        try:
            response = requests.get(url=self._url + ':' + str(self._port),
                                    verify=self._key)
        except requests.exceptions.ConnectionError as e:
            print(e)
            return False
        return response.status_code == 200

    def _download(self):
        response = requests.get(
            url=self._build_url('download'),
            timeout=self._tmt,
            verify=self._key)
        if response.status_code == 200:
            print('downloaded `get_limit` code')
            return response.text
        print('download of `get_limit` code failed')
        print(response.status_code, response.reason)
        return ''

    def _upload_from_file(self, path):
        with open(path, "r") as file:
            response = requests.post(
                url=self._build_url('upload'),
                files={"filename": file},
                timeout=self._tmt,
                verify=self._key)
        if response.status_code == 200:
            print('read and uploaded `get_limit` code from %s' % path)
            return True
        print('uploaded `get_limit` code from %s failed' % path)
        print(response.status_code, response.reason)
        return False

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
