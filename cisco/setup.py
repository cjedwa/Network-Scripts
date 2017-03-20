#!/usr/bin/env python

# instal netmiko & netaddr
from setuptools import setup

setup( name='cisco-commands',
        version='0.1',
        description='Setup cisco-commands',
        author='cody edwards',
        author_email='cody@ydoc.tech',
        install_requires=['netaddr','netmiko', 'pyyaml'],
        )

