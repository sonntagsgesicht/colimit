# -*- coding: utf-8 -*-

# colimit
# -------
# better know your limits
#
# Author:   sonntagsgesicht
# Version:  0.1.9, copyright Monday, 13 September 2021
# Website:  https://sonntagsgesicht.github.com/colimit
# License:  No License - only for h_da staff or students (see LICENSE file)


import os

from colimit import __version__ as VERSION


os.system("auxilium sphinx")
wd = os.getcwd()
os.chdir("doc/sphinx/_build/html")
os.system("zip -r html.zip *")
os.system("mv html.zip " + wd + "/../colimit_app/staging/html-" + VERSION + '.zip')
os.chdir(wd)

os.system("auxilium update")
print("=== build dist ===")
os.system("python3 setup.py sdist --formats=zip")
os.system("cp dist/colimit-" + VERSION + ".zip ../colimit_app/staging")
