#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2021 Andreas Ziegler <andreas.ziegler@fau.de>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os
import sys

from debuginfod.debuginfod import DebugInfoD
from elftools.elf.elffile import ELFFile
from elftools.common.exceptions import ELFError

def _get_buildid(elffile):
    buildid = None
    id_section = elffile.get_section_by_name('.note.gnu.build-id')
    if id_section:
        for note in id_section.iter_notes():
            if note['n_type'] != 'NT_GNU_BUILD_ID':
                continue
            buildid = note['n_desc']
    return buildid

def run(action, arg, sourcefile=None, verbose=False):
    d = DebugInfoD()
    if verbose:
        d.set_verbose_fd(sys.stderr)
    buildid = None
    if all(c in '0123456789abcdef' for c in arg):
        buildid = arg
    else:
        try:
            with open(arg, 'rb') as elffd:
                buildid = _get_buildid(ELFFile(elffd))
        except OSError as e:
            print('Cannot open {}: {}'.format(arg, os.strerror(e.errno)), file=sys.stderr)
        except ELFError as e:
            print('Error while reading ELF file {}: {}'.format(arg, e), file=sys.stderr)
    if buildid is None:
        sys.exit(1)
    if action == 'debuginfo':
        fd, path = d.find_debuginfo(buildid)
    elif action == 'executable':
        fd, path = d.find_executable(buildid)
    elif action == 'source':
        fd, path = d.find_source(buildid, sourcefile)
    if fd < 0:
        print('Query failed: {}'.format(os.strerror(-fd)), file=sys.stderr)
        sys.exit(1)
    print(path.decode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Be more verbose',
                        action='store_true')
    parser.add_argument('action', choices=['debuginfo', 'executable', 'source'],
                        help='The command what to retrieve from debuginfod')
    parser.add_argument('input', nargs='+', help='The build ID')
    args = parser.parse_args()
    if args.action == 'source' and \
            (len(args.input) != 2 or not os.path.isabs(args.input[1])):
        parser.error('Please provide a PATH/BUILDID and an absolute path for \'source\'')
    elif args.action in ('debuginfo', 'executable') and len(args.input) != 1:
        parser.error('Please provide exactly one PATH or BUILDID as a parameter')
    sourcefile = None
    if args.action == 'source':
        sourcefile = args.input[1]

    run(args.action, args.input[0], sourcefile=sourcefile, verbose=args.verbose)
