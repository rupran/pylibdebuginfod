# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: MIT

from setuptools import setup, find_packages

setup(
    name = 'libdebuginfod-python',
    description = 'Python bindings for libdebuginfod',
    author = 'Andreas Ziegler',
    author_email = 'andreas.ziegler@fau.de',
    url = 'https://github.com/rupran/libdebuginfod-python',
    version = '0.1',
    license = 'MIT',
    packages = [
        'debuginfod'
    ]
)
