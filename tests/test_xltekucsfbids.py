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
from pyedflib.highlevel import make_signal_headers, make_header, write_edf, read_edf

# Local Packages #
from src.xltektools.xltekcdfs import XLTEKCDFSEDFExporter
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
    server_path = pathlib.Path("/data_store0/human/converted_clinical")
    server_out_path = pathlib.Path("/scratch/afong/bidstest")
    server_path_kleen = pathlib.Path("/scratch/anthonyfong/ucsfbids")
    server_out_path_kleen = pathlib.Path("/scratch/anthonyfong/bidstest")

    def test_session_creation(self, tmp_path):
        subject = Subject(name="EC0212", parent_path=tmp_path, create=True)
        new_session = subject.create_new_session(XLTEKUCSFBIDSSession, mode="w", create=True)
        assert True

    def test_session_loading(self, tmp_path):
        subject = Subject(name="EC000", parent_path=tmp_path, create=True)
        new_session = subject.create_new_session(XLTEKUCSFBIDSSession, mode="w", create=True)

        subject_copy = Subject(name="EC000", parent_path=tmp_path)
        session = list(subject_copy.sessions.values())[0]

        assert isinstance(session, XLTEKUCSFBIDSSession)

    def test_edf_exporter(self):
        subject = Subject(name="EC0291", parent_path=self.server_path, mode="r")
        session = subject.sessions["S0000"]
        session.require_cdfs(load=True)

        channel_names = list(session.load_electrodes().iloc[:, 1])
        n_channels = len(channel_names)
        if n_channels > 148:
            channel_names.extend((f"BLANK{i + 1}" for i in range(n_channels, 256)))
        else:
            channel_names.extend((f"BLANK{i + 1}" for i in range(n_channels, 128)))
        channel_names.extend((f"DC{i + 1}" for i in range(16)))
        channel_names.extend(("TRIG", "OSAT", "PR", "Pleth"))

        exporter = XLTEKCDFSEDFExporter(session.cdfs, new_name="UPenn0000", channel_names=channel_names)
        exporter.export_as_days(self.server_out_path, name=session.full_name)

    def test_subject_exporter(self):
        subject = Subject(name="EC0212", parent_path=self.server_path_kleen, mode="r")

        exporter = subject.create_exporter("BIDS")
        exporter.export(self.server_out_path_kleen, name="UPenn0000")

    def test_annotation_read(self):
        path = self.server_out_path_kleen / f"UPenn0000_task-day1.edf"
        sigs, sig_headers, header = read_edf(path.as_posix())
        assert header["annotations"]


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])
