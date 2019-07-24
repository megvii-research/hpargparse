#!/usr/bin/env python3
import argparse
import hpargparse
from hpman.m import _
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    parser = argparse.ArgumentParser()

    # ... do whatever you want
    parser.add_argument(dest="predefined_arg")

    # analyze everything in this directory
    _.parse_file(BASE_DIR)  # <-- IMPORTANT

    # bind will monkey_patch parser.parse_args to do its job
    hpargparse.bind(parser, _)  # <-- IMPORTANT

    # parse args and set the values
    args = parser.parse_args()

    # ... do whatever you want next
    import lib

    print("a = {}".format(_.get_value("a")))
    print("b = {}".format(_.get_value("b")))
    print("lib.add() = {}".format(lib.add()))
    print("lib.mult() = {}".format(lib.mult()))


if __name__ == "__main__":
    main()
