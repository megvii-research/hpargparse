import unittest
import hpargparse
import argparse
import libhpman
from pathlib import Path
import contextlib

import os
import shutil
import tempfile

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
test_file_dir = Path(BASE_DIR) / "test_files"


@contextlib.contextmanager
def auto_cleanup_temp_dir():
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix="hpargparse-test"))
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)


class TestAll(unittest.TestCase):
    def _make_basic(self):
        hp_mgr = libhpman.HyperParameterManager("_")
        parser = argparse.ArgumentParser()
        parser.add_argument(dest="predefined_arg")
        hp_mgr.parse_file(test_file_dir / "basic" / "lib.py")
        hpargparse.bind(parser, hp_mgr)
        return parser, hp_mgr

    def test_basic(self):
        parser, hp_mgr = self._make_basic()
        parser.parse_args(["an_arg_value"])

    def test_set_value(self):
        parser, hp_mgr = self._make_basic()
        parser.parse_args(["an_arg_value", "--a", "3"])

    def test_set_value_failure(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--a", "abc"])

    def test_hp_list(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--hp-list"])

    def test_hp_save(self):
        with auto_cleanup_temp_dir() as d:
            parser, hp_mgr = self._make_basic()
            path = str(d / "config.yaml")
            parser.parse_args(["an_arg_value", "--hp-save", path])

    def test_hp_load(self):
        parser, hp_mgr = self._make_basic()
        parser.parse_args(
            ["an_arg_value", "--hp-load", str(test_file_dir / "basic" / "config.yaml")]
        )
