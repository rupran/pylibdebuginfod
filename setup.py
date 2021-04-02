# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: MIT

from setuptools import setup

setup(
    name = 'pylibdebuginfod',
    description = 'Python bindings for libdebuginfod',
    author = 'Andreas Ziegler',
    author_email = 'andreas.ziegler@fau.de',
    url = 'https://github.com/rupran/pylibdebuginfod',
    version = '0.1',
    license = 'MIT',
    packages = [
        'libdebuginfod'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
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
