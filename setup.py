#!/usr/bin/env python

# instal netmiko & netaddr
from setuptools import setup

setup( name='cisco-commands',
        version='0.1',
        description='some cisco switch stuff',
        author='cody edwards',
        author_email='cjedwa@internet.com',
        install_requires=['netaddr','netmiko'],
        )

