#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
	name='pyusbpd',
	version='0.0.1',
	description='Unofficial USB Power Delivery toolbox for Python',
	long_description=long_description,
    long_description_content_type="text/markdown",
	author='Jean THOMAS',
	author_email='virgule@jeanthomas.me',
	license='ISC',
	python_requires=">=3.8",
)
