#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages

curdir = os.path.dirname(os.path.realpath(__file__))
requirements = open(curdir + '/requirements.txt').readlines()
version = open(curdir + '/VERSION').read().strip()

setup(
    name='whoiscache',
    description='Cache service for WHOIS data',
    version=version,
    author='sadler@port-zero.com',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
)
