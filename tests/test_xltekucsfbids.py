#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_xltekucsfbids.py

"""
# Package Header #
from src.xltektools.header import *


# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


import cProfile

# Imports #
# Standard Libraries #
import datetime
import io
import os
import pathlib
import pickle
import pstats
from pstats import Stats, f8, func_std_string
import timeit
import time

import h5py
import numpy as np
import pytest

# Third-Party Packages #
from ucsfbids import Subject, Session

# Local Packages #
from src.xltektools.xltekucsfbids import XLTEKUCSFBIDSSession


# Definitions #
# Functions #
@pytest.fixture
def tmp_dir(tmpdir):
    """A pytest fixture that turn the tmpdir into a Path object."""
    return pathlib.Path(tmpdir)


# Classes #
class ClassTest:
    """Default class tests that all classes should pass."""

    class_ = None
    timeit_runs = 2
    speed_tolerance = 200

    def get_log_lines(self, tmp_dir, logger_name):
        path = tmp_dir.joinpath(f"{logger_name}.log")
        with path.open() as f_object:
            lines = f_object.readlines()
        return lines


class TestXLTEKUCSFBIDS(ClassTest):

    def test_session_creation(self, tmp_path):
        subject = Subject(name="EC000", parent_path=tmp_path, create=True)
        new_session = subject.create_new_session(XLTEKUCSFBIDSSession, mode="w", create=True)
        assert True

    def test_session_loading(self, tmp_path):
        subject = Subject(name="EC000", parent_path=tmp_path, create=True)
        new_session = subject.create_new_session(XLTEKUCSFBIDSSession, mode="w", create=True)

        subject_copy = Subject(name="EC000", parent_path=tmp_path)
        session = list(subject_copy.sessions.values())[0]

        assert isinstance(session, XLTEKUCSFBIDSSession)


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])
