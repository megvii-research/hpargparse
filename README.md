# hpargparse
An argparse extension for [hpman]()

# Installation
```bash
pip install hpargparse
```

# Brief Introduction

The following example lies in [examples/02-brief](./examples/02-brief).

`main.py`
```python
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
```

results in:
```bash
$ ./main.py
weight decay is 1e-05
$ ./main.py --weight-decay 1e-4
weight decay is 0.0001
$ ./main.py --weight-decay 1e-4 --hp-list
weight_decay: 0.0001
$ ./main.py --weight-decay 1e-4 --hp-list detail
All hyperparameters:
    ['weight_decay']
Details:
+--------------+--------+---------+--------------------------------------------------------------+
| name         | type   |   value | details                                                      |
+==============+========+=========+==============================================================+
| weight_decay | float  |  0.0001 | occurrence[0]:                                               |
|              |        |         |   ./main.py:10                                               |
|              |        |         |      5:                                                      |
|              |        |         |      6: import argparse                                      |
|              |        |         |      7:                                                      |
|              |        |         |      8:                                                      |
|              |        |         |      9: def func():                                          |
|              |        |         | ==> 10:     weight_decay = _("weight_decay", 1e-5)           |
|              |        |         |     11:     print("weight decay is {}".format(weight_decay)) |
|              |        |         |     12:                                                      |
|              |        |         |     13:                                                      |
|              |        |         |     14: def main():                                          |
|              |        |         |     15:     parser = argparse.ArgumentParser()               |
+--------------+--------+---------+--------------------------------------------------------------+
$ ./main.py -h
usage: main.py [-h] [--weight-decay WEIGHT_DECAY] [--hp-save HP_SAVE]
               [--hp-load HP_LOAD] [--hp-list [{detail,yaml}]]
               [--hp-serial-format {auto,yaml,pickle}] [--hp-exit]

optional arguments:
  -h, --help            show this help message and exit
  --weight-decay WEIGHT_DECAY
  --hp-save HP_SAVE     Save hyperparameters to a file. The hyperparameters
                        are saved after processing of all other options
  --hp-load HP_LOAD     Load hyperparameters from a file. The hyperparameters
                        are loaded before any other options are processed
  --hp-list [{detail,yaml}]
                        List all available hyperparameters. If `--hp-list
                        detail` is specified, a verbose table will be print
  --hp-serial-format {auto,yaml,pickle}
                        Format of the saved config file. Defaults to auto. Can
                        be set to override auto file type deduction.
  --hp-exit             process all hpargparse actions and quit
```

# hpcli: The Command Line Tool
Besides using `hpargparse.bind` in you code, we also come with a command line
tool `hpcli` to provide similar functions to any existing file using hpman.

`src.py`
```python
from hpman.m import _

_('num_channels', 128)
_('num_layers', 50)
```

In shell:
```bash
$ hpcli src.py
num_channels: 128
num_layers: 50
$ hpcli src.py --num-layers 101
num_channels: 128
num_layers: 101
$ hpcli src.py --num-layers 101 --hp-save config.yaml
num_channels: 128
num_layers: 101
$ hpcli src.py --num-layers 101 --hp-save config.yaml --hp-list detail
All hyperparameters:
    ['num_channels', 'num_layers']
Details:
+--------------+--------+---------+-------------------------------+
| name         | type   |   value | details                       |
+==============+========+=========+===============================+
| num_channels | int    |     128 | occurrence[0]:                |
|              |        |         |   src.py:3                    |
|              |        |         |     1: from hpman.m import _  |
|              |        |         |     2:                        |
|              |        |         | ==> 3: _("num_channels", 128) |
|              |        |         |     4: _("num_layers", 50)    |
|              |        |         |     5:                        |
+--------------+--------+---------+-------------------------------+
| num_layers   | int    |     101 | occurrence[0]:                |
|              |        |         |   src.py:4                    |
|              |        |         |     1: from hpman.m import _  |
|              |        |         |     2:                        |
|              |        |         |     3: _("num_channels", 128) |
|              |        |         | ==> 4: _("num_layers", 50)    |
|              |        |         |     5:                        |
+--------------+--------+---------+-------------------------------+
$ hpcli src.py -h
usage: hpcli [-h] [--num-channels NUM_CHANNELS] [--num-layers NUM_LAYERS]
             [--hp-save HP_SAVE] [--hp-load HP_LOAD]
             [--hp-list [{detail,yaml}]]
             [--hp-serial-format {auto,yaml,pickle}] [--hp-exit]

optional arguments:
  -h, --help            show this help message and exit
  --num-channels NUM_CHANNELS
  --num-layers NUM_LAYERS
  --hp-save HP_SAVE     Save hyperparameters to a file. The hyperparameters
                        are saved after processing of all other options
  --hp-load HP_LOAD     Load hyperparameters from a file. The hyperparameters
                        are loaded before any other options are processed
  --hp-list [{detail,yaml}]
                        List all available hyperparameters. If `--hp-list
                        detail` is specified, a verbose table will be print
  --hp-serial-format {auto,yaml,pickle}
                        Format of the saved config file. Defaults to auto. Can
                        be set to override auto file type deduction.
  --hp-exit             process all hpargparse actions and quit
```

This could be a handy tool to inspect the hyperparameters in your code.

# Example: Deep Learning Experiment
This example lies in [examples/01-nn-training](./examples/01-nn-training).

It is a fully-functional example of training a LeNet on MNIST using
`hpargparse` and `hpman` collaboratively to manage hyperparameters.

We **highly suggest** you playing around this example.


# Example: Basics Walkthrough
Now we break down the functions one-by-one.

The following example lies in [examples/00-basic](./examples/00-basic).

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
```

## Help
```bash
$ ./main.py -h
usage: main.py [-h] [--a A] [--b B] [--hp-save HP_SAVE] [--hp-load HP_LOAD]
               [--hp-list [{detail,yaml}]]
               [--hp-serial-format {auto,yaml,pickle}] [--hp-exit]
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
  --hp-list [{detail,yaml}]
                        List all available hyperparameters. If `--hp-list
                        detail` is specified, a verbose table will be print
  --hp-serial-format {auto,yaml,pickle}
                        Format of the saved config file. Defaults to auto
  --hp-exit             process all hpargparse actions and quit
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
```bash
$ ./main.py some_arg --hp-list
a: 1
b: 2
```
... and details:
```bash
$ ./main.py some_arg --hp-list detail
All hyperparameters:
    ['a', 'b']
Details:
+--------+--------+---------+----------------------------------------------------------------+
| name   | type   |   value | details                                                        |
+========+========+=========+================================================================+
| a      | int    |       1 | occurrence[0]:                                                 |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:8          |
|        |        |         |      3: # for more usecases, please refer to hpman's document  |
|        |        |         |      4:                                                        |
|        |        |         |      5:                                                        |
|        |        |         |      6: def add():                                             |
|        |        |         |      7:     # define a hyperparameter on-the-fly with defaults |
|        |        |         | ==>  8:     return _("a", 1) + _("b", 2)                       |
|        |        |         |      9:                                                        |
|        |        |         |     10:                                                        |
|        |        |         |     11: def mult():                                            |
|        |        |         |     12:     # reuse a pre-defined hyperparameters              |
|        |        |         |     13:     return _("a") * _("b")                             |
|        |        |         | occurrence[1]:                                                 |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:13         |
|        |        |         |      8:     return _("a", 1) + _("b", 2)                       |
|        |        |         |      9:                                                        |
|        |        |         |     10:                                                        |
|        |        |         |     11: def mult():                                            |
|        |        |         |     12:     # reuse a pre-defined hyperparameters              |
|        |        |         | ==> 13:     return _("a") * _("b")                             |
|        |        |         |     14:                                                        |
+--------+--------+---------+----------------------------------------------------------------+
| b      | int    |       2 | occurrence[0]:                                                 |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:8          |
|        |        |         |      3: # for more usecases, please refer to hpman's document  |
|        |        |         |      4:                                                        |
|        |        |         |      5:                                                        |
|        |        |         |      6: def add():                                             |
|        |        |         |      7:     # define a hyperparameter on-the-fly with defaults |
|        |        |         | ==>  8:     return _("a", 1) + _("b", 2)                       |
|        |        |         |      9:                                                        |
|        |        |         |     10:                                                        |
|        |        |         |     11: def mult():                                            |
|        |        |         |     12:     # reuse a pre-defined hyperparameters              |
|        |        |         |     13:     return _("a") * _("b")                             |
|        |        |         | occurrence[1]:                                                 |
|        |        |         |   /data/project/hpargparse/examples/00-basic/lib.py:13         |
|        |        |         |      8:     return _("a", 1) + _("b", 2)                       |
|        |        |         |      9:                                                        |
|        |        |         |     10:                                                        |
|        |        |         |     11: def mult():                                            |
|        |        |         |     12:     # reuse a pre-defined hyperparameters              |
|        |        |         | ==> 13:     return _("a") * _("b")                             |
|        |        |         |     14:                                                        |
+--------+--------+---------+----------------------------------------------------------------+
```

## Save/Load from/to YAML file
```bash
# save to yaml file
$ ./main.py some_arg --hp-save /tmp/config.yaml --hp-exit

$ cat /tmp/config.yaml 
a: 1
b: 2

# load from yaml file
$ cat config_modified.yaml
a: 123
b: 456

$ ./main.py some_arg --hp-load config_modified.yaml --hp-list
a: 123
b: 456
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

