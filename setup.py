#!/usr/bin/env python
#-*-coding:utf8-*-
# python setup.py sdist upload

import os
from setuptools import setup, find_packages

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

#requires = []
#with open('REQUIREMENTS', 'r') as f:
#    requires.extend(f.readlines())

setup(
    name="v7py",
    version="0.1",
    license="GPL",
    description = '1C:Enterprice v7.7 MD reader and SQL parser',
    long_description=read("DESCRIPTION"),
    author="Stoyanov Evgeny",
    author_email="quick.es@gmail.com",
    url="https://github.com/WorldException/v7py",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Database'
    ],
    packages=['v7'],
    keywords='1C 1C:Enterprise 7.7 MD'
)
