#!/usr/bin/env python3
import argparse
import hpargparse
from hpman.m import _
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(dest="predefined_arg")
    # ... do whatever you want

    _.parse_file(BASE_DIR)

    # bind will monkey_patch parser.parse_args to do its job
    hpargparse.bind(parser, _)

    args = parser.parse_args()

    # ... do whatever next
    print(args)


if __name__ == "__main__":
    main()
