import unittest
import hpargparse
import argparse
import pickle
import hpman
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
    def _make(self, fpath):
        fpath = str(fpath)
        hp_mgr = libhpman.HyperParameterManager("_")
        parser = argparse.ArgumentParser()
        parser.add_argument(dest="predefined_arg")
        hp_mgr.parse_file(fpath)
        hpargparse.bind(parser, hp_mgr)
        return parser, hp_mgr

    def _make_basic(self):
        return self._make(test_file_dir / "basic" / "lib.py")

    def _make_dict_and_list(self):
        return self._make(test_file_dir / "dict_and_list" / "lib_dict_and_list.py")

    def test_basic(self):
        parser, hp_mgr = self._make_basic()
        parser.parse_args(["an_arg_value"])

    def test_set_value(self):
        parser, hp_mgr = self._make_basic()
        args = parser.parse_args(["an_arg_value", "--a", "3"])
        self.assertEqual(args.a, 3)
        self.assertEqual(hp_mgr.get_value("a"), 3)

    def test_set_value_failure(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--a", "abc"])

    def test_hp_list(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--hp-list"])

    def test_hp_save(self):
        for name in ["config.yaml", "config.yml", "config.pkl", "config.pickle"]:
            with auto_cleanup_temp_dir() as d:
                parser, hp_mgr = self._make_basic()
                path = str(d / name)
                parser.parse_args(["an_arg_value", "--hp-save", path])

    def test_hp_save_failure(self):
        with auto_cleanup_temp_dir() as d:
            parser, hp_mgr = self._make_basic()
            path = str(d / "a.bcd")
            self.assertRaisesRegex(
                ValueError,
                "Unsupported file extension: .bcd",
                parser.parse_args,
                ["an_arg_value", "--hp-save", path],
            )

    def test_hp_load(self):
        parser, hp_mgr = self._make_basic()
        parser.parse_args(
            ["an_arg_value", "--hp-load", str(test_file_dir / "basic" / "config.yaml")]
        )

        with auto_cleanup_temp_dir() as d:
            parser, hp_mgr = self._make_basic()
            path = str(d / "a.pkl")
            with open(path, "wb") as f:
                pickle.dump({"a": 10, "b": 20}, f)
            parser.parse_args(["an_arg_value", "--hp-load", str(path)])

    def test_hp_load_failure(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaisesRegex(
            TypeError,
            "int\\(\\) argument must be a string, a bytes-like object or a number, not 'dict'",
            parser.parse_args,
            [
                "an_arg_value",
                "--hp-load",
                str(test_file_dir / "basic" / "config.failure.yaml"),
            ],
        )

    def test_set_dict_and_list(self):
        parser, hp_mgr = self._make_dict_and_list()
        args = parser.parse_args(["an_arg_value", "--a", '{"key": 3}'])
        self.assertDictEqual(args.a, {"key": 3})
        self.assertDictEqual(hp_mgr.get_value("a"), {"key": 3})

    def test_set_dict_and_list_failure(self):
        parser, hp_mgr = self._make_dict_and_list()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--a", "1"])

    def test_hp_load_dict_and_list(self):
        parser, hp_mgr = self._make_dict_and_list()
        parser.parse_args(
            [
                "an_arg_value",
                "--hp-load",
                str(test_file_dir / "dict_and_list" / "config.yaml"),
            ]
        )
