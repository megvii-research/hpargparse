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
    """
    :return: a `class`:`pathlib.Path` object 
    """
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix="hpargparse-test"))
        yield tmpdir
    finally:
        shutil.rmtree(str(tmpdir))


class TestAll(unittest.TestCase):
    def _make(self, fpath):
        fpath = str(fpath)
        hp_mgr = hpman.HyperParameterManager("_")
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
        self.assertRaises(
            SystemExit, parser.parse_args, ["an_arg_value", "--hp-list", "detail"]
        )
        self.assertRaises(
            SystemExit, parser.parse_args, ["an_arg_value", "--hp-list", "json"]
        )
    
    def test_hp_detail(self):
        parser, hp_mgr = self._make_basic()
        self.assertRaises(SystemExit, parser.parse_args, ["an_arg_value", "--hp-detail"])

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
        # test load yaml
        parser, hp_mgr = self._make_basic()
        parser.parse_args(
            ["an_arg_value", "--hp-load", str(test_file_dir / "basic" / "config.yaml")]
        )

        # test load pickle
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
        self.assertDictEqual(hp_mgr.get_value("a"), {"key": 3})
        self.assertListEqual(hp_mgr.get_value("b"), [2, 3, 4])

    def test_hp_load_dict_and_list_with_cmd_set(self):
        parser, hp_mgr = self._make_dict_and_list()
        parser.parse_args(
            [
                "an_arg_value",
                "--hp-load",
                str(test_file_dir / "dict_and_list" / "config.yaml"),
                "--a",
                '{"a": 1}',
                "--b",
                "[1, 2, 3]",
                "--c",
                "42",
            ]
        )
        self.assertDictEqual(hp_mgr.get_value("a"), {"a": 1})
        self.assertListEqual(hp_mgr.get_value("b"), [1, 2, 3])
        self.assertEqual(hp_mgr.get_value("c"), 42)

    def _make_pair(self):
        hp_mgr = hpman.HyperParameterManager("_")
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        hp_mgr.parse_source('_("a", 1)')
        return hp_mgr, parser

    def test_bind_actions(self):
        def do_test(assert_type, regex, **bind_kwargs):
            hp_mgr, parser = self._make_pair()
            hpargparse.bind(parser, hp_mgr, **bind_kwargs)

            assertion = {True: self.assertRegex, False: self.assertNotRegex}[
                assert_type
            ]
            assertion(parser.format_help(), regex)

        all_keys = ["save", "load", "list", "detail", "serial-format", "exit"]

        def test_exist(keywords, **bind_kwargs):

            not_exists = all_keys.copy()
            for k in keywords:
                assert k in all_keys, (k, all_keys)
                not_exists.remove(k)

            exist_regex = "|".join("-{}".format(k) for k in keywords)
            not_exist_regex = "|".join("-{}".format(k) for k in not_exists)

            assert (set(keywords) | set(not_exists)) == set(all_keys)

            if exist_regex:
                do_test(True, exist_regex, **bind_kwargs)
            if not_exist_regex:
                do_test(False, not_exist_regex, **bind_kwargs)

        test_exist(all_keys)
        test_exist([], inject_actions=False)
        test_exist(["save", "serial-format", "exit"], inject_actions=["save"])
        test_exist(["load", "serial-format", "exit"], inject_actions=["load"])
        test_exist(
            ["save", "load", "serial-format", "exit"], inject_actions=["save", "load"]
        )
        test_exist(["list", "exit"], inject_actions=["list"])
        test_exist(
            ["save", "serial-format", "list", "exit"], inject_actions=["save", "list"]
        )
        test_exist(
            ["load", "serial-format", "list", "exit"], inject_actions=["load", "list"]
        )
        test_exist(
            ["save", "load", "serial-format", "list", "exit"],
            inject_actions=["save", "load", "list"],
        )

    def test_bind_action_prefix(self):
        hp_mgr, parser = self._make_pair()
        hpargparse.bind(parser, hp_mgr, action_prefix="hahaha")
        self.assertRegex(parser.format_help(), r"--hahaha-")

    def test_bind_serial_format(self):
        hp_mgr, parser = self._make_pair()
        hpargparse.bind(parser, hp_mgr, serial_format="pickle")

        with auto_cleanup_temp_dir() as d:
            path = d / "a.pkl"
            parser.parse_args(["--hp-save", str(path)])

            with open(str(path), "rb") as f:
                x = pickle.load(f)

            self.assertEqual(x["a"], 1)

    def test_show_default_value_in_help_message(self):
        hp_mgr, parser = self._make_pair()
        hp_mgr.parse_source("_('b', True)")
        hp_mgr.parse_source("_('c', 'deadbeef')")
        hpargparse.bind(parser, hp_mgr)

        h = parser.format_help()
        self.assertRegex(h, "default: 1")
        self.assertRegex(h, "default: True")
        self.assertRegex(h, "default: deadbeef")
