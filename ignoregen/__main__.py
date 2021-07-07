##################################################
# Copyright (C) 2017-2020, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import os
import sys

from pyprelude.file_system import make_path
from pysimplevcs.git import Git

from ignoregen import __description__, __project_name__, __version__

LOCAL_HOME_DIR = os.environ.get("USERPROFILE") or os.path.expanduser("~")

def _remove_prefix(prefix, s):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return None

def _get_names_to_ignore(search_dir, truncate=None):
    git = Git(search_dir)
    dir_names = set()
    file_names = set()
    for line in git.status("--ignored").decode("utf-8").splitlines():
        temp = _remove_prefix("#", line)
        if temp is None:
            temp = _remove_prefix("\t", line)
            if temp is None: continue

        temp = temp.strip()
        if len(temp) == 0: continue

        parts = temp.split("/")[:truncate]
        if len(parts[-1]) == 0: parts.pop()

        name = "/".join(parts)
        path = make_path(search_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            file_names.add(name)
        if os.path.isdir(path):
            dir_names.add(name)

    return dir_names, file_names

def _do_gen(args):
    dir_names, file_names = _get_names_to_ignore(LOCAL_HOME_DIR, args.truncate)
    print("# Automatically generated by {} version {}".format(__project_name__, __version__))
    if args.truncate is not None:
        print("# --truncate={}".format(args.truncate))
    print()

    print("# Directories")
    for n in sorted(dir_names):
        print("/{}/".format(n))
    print()

    print("# Files and symlinks")
    for n in sorted(file_names):
        print("/{}".format(n))

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog=__project_name__, description=__description__)
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))

    subparsers = parser.add_subparsers(help="subcommand help")

    gen_parser = subparsers.add_parser("gen", help="Generate Git ignore rules")
    gen_parser.set_defaults(func=_do_gen)
    gen_parser.add_argument("--truncate", "-t", type=int, default=1, help="Truncate paths to specified level")

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    _main()
