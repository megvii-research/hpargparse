# hpargparse
An argparse extension for [hpman]()

# Installation
```bash
pip install hpargparse
```

# Example

The example below lies [here](./examples/00-basic)

`lib.py`:
```python
from hpman.m import _


def add():
    return _("a", 1) + _("b", 2)


def mult():
    return _("a") * _("b")
```

`main.py`
```python
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

    # analyze everything in this directory
    _.parse_file(BASE_DIR)

    # bind will monkey_patch parser.parse_args to do its job
    hpargparse.bind(parser, _)

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
```

## Help
```bash
usage: main.py [-h] [--a A] [--b B] [--hp-save HP_SAVE] [--hp-load HP_LOAD]
               [--hp-list] [--hp-serial-format {auto,yaml,pickle}]
               [--hp-dry-run]
               predefined_arg

positional arguments:
  predefined_arg

optional arguments:
  -h, --help            show this help message and exit
  --a A
  --b B
  --hp-save HP_SAVE     Save hyperparameters to a file. The hyperparameters
                        are saved after processing of all other options
  --hp-load HP_LOAD     Load hyperparameters from a file. The hyperparameters
                        are loaded before any other options are processed
  --hp-list             List all available hyperparameters
  --hp-serial-format {auto,yaml,pickle}
                        Format of the saved config file. Defaults to auto
  --hp-dry-run          process all hpargparse actions and quit
```


## Set Hyperparameters from Command Line Arguments
```bash
$ ./main.py some_thing --a 3 --b 5
a = 3
b = 5
lib.add() = 8
lib.mult() = 15
```


## List All Hyperparameters 
... as well as their occurrence:

```bash
$ ./main.py some_thing --hp-list
All hyperparameters:
    ['a', 'b']
Details:
+--------+--------+---------+-------------------------------------------------------+
| name   | type   |   value | details                                               |
+========+========+=========+=======================================================+
| a      | int    |       1 | occurrence[0]:                                        |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:5 |
|        |        |         |     1: from hpman.m import _                          |
|        |        |         |     2:                                                |
|        |        |         |     3:                                                |
|        |        |         |     4: def add():                                     |
|        |        |         | ==> 5:     return _("a", 1) + _("b", 2)               |
|        |        |         |     6:                                                |
|        |        |         |     7:                                                |
|        |        |         |     8: def mult():                                    |
|        |        |         |     9:     return _("a") * _("b")                     |
|        |        |         |     10:                                               |
|        |        |         | occurrence[1]:                                        |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:9 |
|        |        |         |     4: def add():                                     |
|        |        |         |     5:     return _("a", 1) + _("b", 2)               |
|        |        |         |     6:                                                |
|        |        |         |     7:                                                |
|        |        |         |     8: def mult():                                    |
|        |        |         | ==> 9:     return _("a") * _("b")                     |
|        |        |         |     10:                                               |
+--------+--------+---------+-------------------------------------------------------+
| b      | int    |       2 | occurrence[0]:                                        |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:5 |
|        |        |         |     1: from hpman.m import _                          |
|        |        |         |     2:                                                |
|        |        |         |     3:                                                |
|        |        |         |     4: def add():                                     |
|        |        |         | ==> 5:     return _("a", 1) + _("b", 2)               |
|        |        |         |     6:                                                |
|        |        |         |     7:                                                |
|        |        |         |     8: def mult():                                    |
|        |        |         |     9:     return _("a") * _("b")                     |
|        |        |         |     10:                                               |
|        |        |         | occurrence[1]:                                        |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:9 |
|        |        |         |     4: def add():                                     |
|        |        |         |     5:     return _("a", 1) + _("b", 2)               |
|        |        |         |     6:                                                |
|        |        |         |     7:                                                |
|        |        |         |     8: def mult():                                    |
|        |        |         | ==> 9:     return _("a") * _("b")                     |
|        |        |         |     10:                                               |
+--------+--------+---------+-------------------------------------------------------+
```

# Development
1. Install requirements:
```
pip install -r requirements.dev.txt -r requirements.txt
```

2. Install pre-commit hook
```
pre-commit install
```

