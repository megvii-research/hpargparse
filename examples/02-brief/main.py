#!/usr/bin/env python3

from hpman.m import _
import hpargparse

import argparse


def func():
    weight_decay = _("weight_decay", 1e-5)
    print("weight decay is {}".format(weight_decay))


def main():
    parser = argparse.ArgumentParser()
    _.parse_file(__file__)
    hpargparse.bind(parser, _)
    parser.parse_args()

    func()


if __name__ == "__main__":
    main()
