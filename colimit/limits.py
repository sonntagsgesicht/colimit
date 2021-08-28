# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
# 
# Author:   Jan-Philipp Hoffmann
# Version:  0.1.6, copyright Friday, 27 August 2021
# Website:  https://code.fbi.h-da.de/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import os
import requests

from .location import Location
from .way import Way

__all__ = "Connection",

URL = "http://limits.pythonanywhere.com"
PORT = "80"
TIMEOUT = 180
METHODS_WITH_SECRET = 'upload', 'download'


class Connection(object):

    def __init__(self, username, password,
                 url=URL, port=PORT, verify=True,
                 timeout=TIMEOUT):
        self._usr = username
        self._pwd = password
        self._url = url
        self._port = port
        self._tmt = timeout
        print('connect as "%s" to %s:%s' % (username, url, port))
        self._func = ''
        self._key = verify
        if self._ping():
            self._func = self._download()
        else:
            print('%s:%s is offline' % (url, port))

    @property
    def get_limit_code(self):
        return str(self._func)

    # -- public methods ---

    def update_get_limit_code(self, path):
        if os.path.exists(path):
            if not self._upload_from_file(path):
                raise AssertionError("Code update failed.")
            if not self._validate_with_file(path):
                raise AssertionError("Code validation failed.")
        else:
            if not self._download_to_file(path):
                raise AssertionError("Code download failed.")
        with open(path, 'r') as f:
            self._func = f.read()
        return self.get_limit_code

    def get_limit(self, latitude=None, longitude=None,
                  speed=None, direction=None, location=None):
        if location:
            latitude = location.latitude
            longitude = location.longitude
            speed = location.speed
            direction = location.direction
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
                 force=False, timeout=None):
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
            "force": force
        }
        response = requests.post(
            url=self._build_url('get_ways'),
            json=kwargs,
            timeout=self._tmt)
        if not response.status_code == 200:
            raise ConnectionError(response.text)
        result = response.json()
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
