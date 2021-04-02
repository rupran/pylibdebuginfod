# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: MIT

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'pylibdebuginfod',
    description = 'Python bindings for libdebuginfod',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Andreas Ziegler',
    author_email = 'andreas.ziegler@fau.de',
    url = 'https://github.com/rupran/pylibdebuginfod',
    version = '0.1',
    license = 'MIT',
    packages = [
        'libdebuginfod'
    ],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
