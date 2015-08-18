#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages


requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),\
                                 'requirements.txt')

setup(
    name='whoiscache',
    description='Cache service for WHOIS data',
    version=__import__('whoiscache').__version__,
    author='sadler@port-zero.com',
    packages=find_packages(),
    install_requires=open(requirements_path).readlines(),
    include_package_data=True,
)
