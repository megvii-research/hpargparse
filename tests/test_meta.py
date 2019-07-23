import unittest
import hpargparse
import argparse
import libhpman
from pathlib import Path

import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
test_file_dir = Path(BASE_DIR) / "test_files"


class Test(unittest.TestCase):
    def test_basic(self):
        pass
