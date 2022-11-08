# logistics
import subprocess
import sys
import ast

import argparse
import functools
import dill
import yaml
import json
import collections
import os
from copy import deepcopy

from types import MethodType

import hpman
from hpman import (
    HyperParameterManager,
    HyperParameterOccurrence,
    SourceHelper,
    EmptyValue,
)

from . import config

from typing import Union, List


from rich.console import Console
from rich.table import Column, Table
from rich.syntax import Syntax
from rich.style import Style
from rich import box


class StringAsDefault(str):
    """If a string is used as parser.add_argument(default=string),
    this string should be mark as StringAsDefault
    """

    pass


def list_of_dict2tab(list_of_dict, headers):
    """Convert "a list of dict" to "a list of list" that suitable
    for table processing libraries (such as tabulate)

    :params list_of_dict: input data
    :params headers: a list of str, header items with order

    :return: list of list of objects
    """
    rows = [[dct[h] for h in headers] for dct in list_of_dict]
    return rows


def make_detail_str(details):
    """
    :param details: List of details. A detail is either a string
        or a list of strings, each one comprises a line

    :return: a string, the formatted detail
    """
    strs = []
    for d in details:
        if isinstance(d["detail"], str):
            ds = [d["detail"]]
        else:
            assert isinstance(d["detail"], (list, tuple)), d["detail"]
            ds = d["detail"]

        s = "\n".join(["{}:".format(d["name"])] + ["  " + line for line in ds])
        strs.append(s)
        strs.append("\n")

    return "".join(strs)


def make_value_illu(v):
    """Mute non-literal-evaluable values

    :return: None if v is :class:`hpman.NotLiteralEvaluable`,
        otherwise the original input.
    """
    if isinstance(v, hpman.NotLiteralEvaluable):
        return None
    return v


def hp_list(mgr):
    """Print hyperparameter settings to stdout"""

    syntax = Syntax(
        "All hyperparameters:\n" + "    {}".format(sorted(mgr.get_values().keys())),
        "python",
        theme="monokai",
    )
    console = Console()
    console.print(syntax)

    # construct a table
    console = Console()
    table = Table(
        title="Details",
        title_style=Style(color="bright_cyan", bgcolor="grey15", bold=True),
        style=Style(bgcolor="grey15"),
        header_style="bold magenta",
        box=box.DOUBLE,
        border_style="bright_cyan",
        show_lines=True,
    )
    table.add_column("name", style="green_yellow")
    table.add_column("type", style="light_steel_blue")
    table.add_column("value", style="light_cyan1")
    table.add_column("details")

    """
    for k, d in sorted(mgr.db.group_by("name").items()):
        details = []
        for i, oc in enumerate(
            d.select(L.exist_attr("filename")).sorted(L.order_by("filename"))
        ):
            # make context detail
            details.append(
                {
                    "name": "occurrence[{}]".format(i),
                    "detail": SourceHelper.format_given_filepath_and_lineno(
                        oc.filename, oc.lineno
                    ),
                }
            )

        # combine details
        detail_str = make_detail_str(details)
        oc = d.sorted(L.value_priority)[0]
        detail_syntax = Syntax(detail_str, "python", theme="monokai")
        table.add_row(
            k,
            str(type(oc.value).__name__),
            str(make_value_illu(oc.value)),
            detail_syntax,
        )
        """

    for node in sorted(mgr.tree.flatten(), key=lambda x: x.name):
        details = []
        for i, oc in enumerate(sorted(node.db, key=lambda x: x.filename)):
            # make context detail
            details.append(
                {
                    "name": "occurrence[{}]".format(i),
                    "detail": SourceHelper.format_given_filepath_and_lineno(
                        oc.filename, oc.lineno
                    ),
                }
            )

        # combine details
        detail_str = make_detail_str(details)
        detail_syntax = Syntax(detail_str, "python", theme="monokai")
        table.add_row(
            node.name,
            str(type(node.value).__name__),
            str(make_value_illu(node.value)),
            detail_syntax,
        )

    console.print(table)


def parse_action_list(inject_actions: Union[bool, List[str]]) -> List[str]:
    """Parse inputs to inject actions.

    :param inject_actions: see :func:`.bind` for detail
    :return: a list of action names
    """
    if isinstance(inject_actions, bool):
        inject_actions = {True: ["save", "load", "list", "detail"], False: []}[
            inject_actions
        ]
    return inject_actions


def _get_argument_type_by_value(value):
    typ = type(value)
    if isinstance(value, (list, dict)):

        def type_func(s):
            if isinstance(s, typ):
                eval_val = s
            else:
                assert isinstance(s, str), type(s)
                eval_val = ast.literal_eval(s)

            if not isinstance(eval_val, typ):
                raise TypeError("value `{}` is not of type {}".format(eval_val, typ))
            return eval_val

        return type_func
    return typ


def str2bool(v):
    """Parsing a string into a bool type.

    :param v: A string that needs to be parsed.

    :return: True or False
    """
    if v.lower() in ["yes", "true", "t", "y", "1"]:
        return True
    elif v.lower() in ["no", "false", "f", "n", "0"]:
        return False
    else:
        raise argparse.ArgumentTypeError("Unsupported value encountered.")


def inject_args(
    parser: argparse.ArgumentParser,
    hp_mgr: hpman.HyperParameterManager,
    *,
    inject_actions: List[str],
    action_prefix: str,
    serial_format: str,
    show_defaults: bool,
) -> argparse.ArgumentParser:
    """Inject hpman parsed hyperparameter settings into argparse arguments.
    Only a limited set of format are supported. See code for details.

    :param parser: Use given parser object of `class`:`argparse.ArgumentParser`.
    :param hp_mgr: A `class`:`hpman.HyperParameterManager` object.

    :param inject_actions: A list of actions names to inject
    :param action_prefix: Prefix for hpargparse related options
    :param serial_format: One of 'yaml' and 'pickle'
    :param show_defaults: Show default values

    :return: The injected parser.
    """

    if show_defaults:
        parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

        # Default value will be shown when using argparse.ArgumentDefaultsHelpFormatter
        # only if a help message is present. This is the behavior of argparse.

    value_names_been_set = set()

    def _make_value_names_been_set_injection(name, func):
        @functools.wraps(func)
        def wrapper(string):
            # when isinstance(default, string),
            # the `parser.parse_args()` will run type(default) automaticly.
            # value_names_been_set should ignore these names.
            if not isinstance(string, StringAsDefault):
                value_names_been_set.add(name)
            return func(string)

        return wrapper

    def get_node_attr(node, attr_name):
        for oc in node.db:
            if hasattr(oc, attr_name):
                return getattr(oc, attr_name)

            if attr_name in oc.hints:
                return oc.hints[attr_name]

        return None

    # add options for collected hyper-parameters
    for node in hp_mgr.get_nodes():
        k = get_node_attr(node, "name")
        v = node.get().value

        # this is just a simple hack
        option_name = "--{}".format(k.replace("_", "-"))

        value_type = _get_argument_type_by_value(v)
        type_str = value_type.__name__
        help = (
            get_node_attr(node, "help") or f"A {type_str} hyper-parameter named `{k}`."
        )
        choices = get_node_attr(node, "choices")
        required = get_node_attr(node, "required")
        other_kwargs = {
            "choices": choices,
            "required": required,
            "help": help,
        }

        if value_type == bool:
            # argparse does not directly support bool types.
            other_kwargs.update(choices=["True", "False"])
            parser.add_argument(
                option_name,
                type=_make_value_names_been_set_injection(k, str2bool),
                default=v,
                **other_kwargs,
            )
        else:
            if isinstance(v, str):
                # if isinstance(v, str), mark as StringAsDefault
                v = StringAsDefault(v)

            parser.add_argument(
                option_name,
                type=_make_value_names_been_set_injection(
                    k, _get_argument_type_by_value(v)
                ),
                default=v,
                **other_kwargs,
            )

    make_option = lambda name: "--{}-{}".format(action_prefix, name)

    for action in inject_actions:
        if action == "list":
            parser.add_argument(
                make_option("list"),
                action="store",
                default=None,
                const="yaml",
                nargs="?",
                choices=["detail", "yaml", "json"],
                help=(
                    "List all available hyperparameters. If `{} detail` is"
                    " specified, a verbose table will be print"
                ).format(make_option("list")),
            )
        elif action == "detail":
            parser.add_argument(
                make_option("detail"),
                action="store_true",
                help="Shorthand for --hp-list detail",
            )
        elif action == "save":
            parser.add_argument(
                make_option("save"),
                help=(
                    "Save hyperparameters to a file. The hyperparameters"
                    " are saved after processing of all other options"
                ),
            )

        elif action == "load":
            parser.add_argument(
                make_option("load"),
                help=(
                    "Load hyperparameters from a file. The hyperparameters"
                    " are loaded before any other options are processed"
                ),
            )

    if "load" in inject_actions or "save" in inject_actions:
        parser.add_argument(
            make_option("serial-format"),
            default=serial_format,
            choices=config.HP_SERIAL_FORMAT_CHOICES,
            help=(
                "Format of the saved config file. Defaults to {}."
                " It can be set to override auto file type deduction."
            ).format(serial_format),
        )

    if inject_actions:
        parser.add_argument(
            make_option("exit"),
            action="store_true",
            help="process all hpargparse actions and quit",
        )

    def __hpargparse_value_names_been_set(self):
        return value_names_been_set

    parser.__hpargparse_value_names_been_set = MethodType(
        __hpargparse_value_names_been_set, parser
    )

    return parser


def _infer_file_format(path):
    name, ext = os.path.splitext(path)
    supported_exts = {
        ".yaml": "yaml",
        ".yml": "yaml",
        ".pickle": "pickle",
        ".pkl": "pickle",
    }

    if ext in supported_exts:
        return supported_exts[ext]
    raise ValueError(
        "Unsupported file extension: {} of path {}".format(ext, path),
        "Supported file extensions: {}".format(
            ", ".join("`{}`".format(i) for i in sorted(supported_exts))
        ),
    )


def hp_save(path: str, hp_mgr: hpman.HyperParameterManager, serial_format: str):
    """Save(serialize) hyperparamters.

    :param path: Where to save
    :param hp_mgr: The HyperParameterManager to be saved.
    :param serial_format: The saving format.

    :see: :func:`.bind` for more detail.
    """
    values = hp_mgr.get_values()

    if serial_format == "auto":
        serial_format = _infer_file_format(path)

    if serial_format == "yaml":
        with open(path, "w") as f:
            yaml.dump(values, f)
    else:
        assert serial_format == "pickle", serial_format
        with open(path, "wb") as f:
            dill.dump(values, f)


def hp_load(path, hp_mgr, serial_format):
    """Load(deserialize) hyperparamters.

    :param path: Where to load
    :param hp_mgr: The HyperParameterManager to be set.
    :param serial_format: The saving format.

    :see: :func:`.bind` for more detail.
    """
    if serial_format == "auto":
        serial_format = _infer_file_format(path)

    if serial_format == "yaml":
        with open(path, "r") as f:
            values = yaml.safe_load(f)
    else:
        assert serial_format == "pickle", serial_format
        with open(path, "rb") as f:
            values = dill.load(f)

    old_values = hp_mgr.get_values()
    new_values = {}
    for k, v in values.items():
        if k in old_values:
            old_v = old_values[k]
            try:
                new_values[k] = _get_argument_type_by_value(old_v)(v)
            except TypeError as e:
                e.args = ("Error parsing hyperparameter `{}`".format(k),) + e.args
                raise

    hp_mgr.set_values(new_values)


def bind(
    parser: argparse.ArgumentParser,
    hp_mgr: hpman.HyperParameterManager,
    *,
    inject_actions: Union[bool, List[str]] = True,
    action_prefix: str = config.HP_ACTION_PREFIX_DEFAULT,
    serial_format: str = config.HP_SERIAL_FORMAT_DEFAULT,
    show_defaults: bool = True,
):
    """Bridging the gap between argparse and hpman. This is
        the most important method. Once bounded, hpargparse
        will do the rest for you.

    :param parser: A `class`:`argparse.ArgumentParser` object
    :param hp_mgr: The hyperparameter manager from `hpman`. It is
        usually an 'underscore' variable obtained by `from hpman.m import _`
    :param inject_actions: A list of actions names to inject, or True, to
        inject all available actions. Available actions are 'save', 'load',
        'detail' and 'list'
    :param action_prefix: Prefix for options of hpargparse injected additional
        actions. e.g., the default action_prefix is 'hp'. Therefore, the
        command line options added by :func:`.bind` will be '--hp-save',
        '--hp-load', '--hp-list', etc.
    :param serial_format: One of 'auto', 'yaml' and 'pickle'. Defaults to
        'auto'.  In most cases you need not to alter this argument as long as
        you give the right file extension when using save and load action. To
        be specific, '.yaml' and '.yml' would be deemed as yaml format, and
        '.pickle' and '.pkl' would be seen as pickle format.
    :param show_defaults: Show the default value in help messages.

    :note: pickle is done by `dill` to support pickling of more types.
    """

    # make action list to be injected
    inject_actions = parse_action_list(inject_actions)

    args_set_getter = inject_args(
        parser,
        hp_mgr,
        inject_actions=inject_actions,
        action_prefix=action_prefix,
        serial_format=serial_format,
        show_defaults=show_defaults,
    )

    # hook parser.parse_known_args
    parser._original_parse_known_args = parser.parse_known_args

    def new_parse_known_args(self, *args, **kwargs):
        args, extras = self._original_parse_known_args(*args, **kwargs)

        get_action_value = lambda name: getattr(
            args, "{}_{}".format(action_prefix, name)
        )

        # load saved hyperparameter instance
        load_value = get_action_value("load")
        if "load" in inject_actions and load_value is not None:
            hp_load(load_value, hp_mgr, serial_format)

        # set hyperparameters set from command lines
        old_values = hp_mgr.get_values()
        for k in self.__hpargparse_value_names_been_set():
            v = old_values[k]
            assert hasattr(args, k)
            t = getattr(args, k)
            if isinstance(t, StringAsDefault):
                t = str(t)
            hp_mgr.set_value(k, t)

        save_value = get_action_value("save")
        if "save" in inject_actions and save_value is not None:
            hp_save(save_value, hp_mgr, serial_format)

        # `--hp-detail`` need to preceed `--hp-list`` because `--hp-list detail`
        # will be set by default.
        if "detail" in inject_actions and get_action_value("detail"):
            hp_list(hp_mgr)
            sys.exit(0)

        hp_list_value = get_action_value("list")
        if "list" in inject_actions and hp_list_value is not None:
            if hp_list_value == "yaml":
                syntax = Syntax(
                    yaml.dump(hp_mgr.get_values()).replace("\n\n", "\n"),
                    "yaml",
                    theme="monokai",
                )
                console = Console()
                console.print(syntax)
            elif hp_list_value == "json":
                syntax = Syntax(
                    json.dumps(hp_mgr.get_values()), "json", theme="monokai"
                )
                console = Console()
                console.print(syntax)
            else:
                assert hp_list_value == "detail", hp_list_value
                hp_list(hp_mgr)

            sys.exit(0)

        if inject_actions and get_action_value("exit"):
            sys.exit(0)

        return args, extras

    parser.parse_known_args = MethodType(new_parse_known_args, parser)
