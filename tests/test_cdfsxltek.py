#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_hdf5xltek.py

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
import timeit

import h5py
import numpy as np
import pytest

# Third-Party Packages #
from classversioning import TriNumberVersion
from classversioning import Version
from classversioning import VersionType
from dspobjects.time import Timestamp

# Local Packages #
from src.xltektools.xltekcdfs import XLTEKCDFS
from src.xltektools.xltekcdfs import XLTEKContentsFile


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


class TestCDFSXLTEK(ClassTest):
    class_ = XLTEKCDFS
    studies_path = pathlib.Path("/common/xltek/subjects")
    server_path = pathlib.Path("/data_store0/human/converted_clinical")
    mount_path = pathlib.Path("/mnt/changserver/data_store0/human/converted_clinical")
    load_path = pathlib.Path("/common/xltek/subjects/")
    save_path = pathlib.Path("~/Documents/Projects/Epilepsy Spike Detection")

    def test_load_study(self):
        s_id = "EC283"
        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        assert True

    def test_load_study_profile(self):
        s_id = "EC283"
        pr = cProfile.Profile()
        pr.enable()

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        study_frame.close()
        assert 1

    def test_load_study_server(self):
        s_id = "EC283"
        study_frame = self.class_(s_id=s_id, studies_path=self.server_path)
        assert 1

    def test_get_data(self):
        s_id = "EC283"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        data = study_frame[slice(0, 1)]

        assert data is not None

    def test_get_study_time(self):
        s_id = "EC283"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        dt = study_frame.get_time(-1)

        assert dt == study_frame.end

    def test_get_time_range(self):
        s_id = "EC283"
        first = datetime.datetime(2020, 9, 22, 0, 00, 00)
        second = datetime.datetime(2020, 9, 22, 0, 10, 00)

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        data = study_frame.get_time_range(first, second, aprox=True)

        assert data is not None

    def test_get_timestamp_range_time_profile(self):
        s_id = "EC283"
        first = datetime.datetime(2020, 1, 31, 20, 38, 43, 653012)
        second = datetime.datetime(2020, 1, 31, 20, 48, 43, 653012)
        pr = cProfile.Profile()
        pr.enable()

        with self.class_(s_id=s_id, studies_path=self.studies_path) as study_frame:
            data = study_frame.find_data_range(first, second, approx=True)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        assert data is not None

    def test_find_data_range_time(self):
        s_id = "EC283"
        first = datetime.datetime(2020, 1, 28, 0, 00, 00)
        second = datetime.datetime(2020, 1, 28, 0, 00, 10)
        with self.class_(s_id=s_id, studies_path=self.studies_path) as study_frame:
            data_object1 = study_frame.find_data_range(first, second, approx=True)
            pr = cProfile.Profile()
            pr.enable()

            data_object = study_frame.find_data_range(first, second, approx=True)

            pr.disable()
            s = io.StringIO()
            sortby = pstats.SortKey.TIME
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())

        assert data_object.data is not None

    def test_find_data_range_time_full(self):
        s_id = "EC283"
        first = datetime.datetime(2020, 1, 28, 0, 00, 00)
        second = datetime.datetime(2020, 1, 28, 0, 00, 10)

        pr = cProfile.Profile()
        pr.enable()

        with self.class_(s_id=s_id, studies_path=self.studies_path) as study_frame:
            data_object = study_frame.find_data_range(first, second, approx=True)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        assert data_object.data is not None

    def test_open_study_server_profile(self):
        s_id = "EC283"
        pr = cProfile.Profile()
        pr.enable()

        cdfs = self.class_(path=self.server_path / s_id, open_=True, load=True)
        cdfs.close()

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    def test_data_range_time_server_profile_second(self):
        s_id = "EC288"
        first = datetime.datetime(1970, 1, 7, 0, 10, 0, 653012, tzinfo=datetime.timezone.utc)
        second = datetime.datetime(1970, 1, 7, 1, 10, 0, 653012, tzinfo=datetime.timezone.utc)

        cdfs = self.class_(path=self.server_path / s_id, open_=True, load=True)

        pr = cProfile.Profile()
        pr.enable()

        data = cdfs.data.find_data_range(first, second, approx=True)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        cdfs.close()

    def test_data_range_time_server_profile_hour(self):
        s_id = "EC283"
        first = datetime.datetime(1970, 1, 7, 0, 10, 0, 653012, tzinfo=datetime.timezone.utc)
        second = datetime.datetime(1970, 1, 7, 1, 10, 0, 653012, tzinfo=datetime.timezone.utc)

        cdfs = self.class_(path=self.server_path / s_id, open_=True, load=True)

        pr = cProfile.Profile()
        pr.enable()

        data = cdfs.data.find_data_range(first, second, approx=True)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        cdfs.close()

    def test_date_range_time_one_second(self):
        s_id = "EC283"
        timestamps = [
            {
                "first": datetime.datetime(2020, 1, 31, 20, 38, 43, 653012),
                "second": datetime.datetime(2020, 1, 31, 20, 38, 53, 653012),
            }
        ]
        pr = cProfile.Profile()
        pr.enable()

        study_frame = self.class_(s_id=s_id, studies_path=self.server_path)
        for timestamp in timestamps:
            data = study_frame.find_data_range(timestamp["first"], timestamp["second"], approx=True)
        study_frame.close()

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    def test_validate_shape(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        valid = study_frame.validate_shape()

        assert valid

    def test_shapes(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        shapes = study_frame.shapes

        assert shapes is not None

    def test_shape(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        shape = study_frame.shape

        assert shape is not None

    def test_validate_sample_rate(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        valid = study_frame.validate_sample_rate()

        assert valid

    def test_sample_rates(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        sample_rates = study_frame.sample_rates

        assert sample_rates

    def test_sample_rate(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        sample_rate = study_frame.sample_rate

        assert sample_rate

    def test_where_discontinuous(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        discontinuities = study_frame.where_discontinuous()

        assert discontinuities is not None

    def test_validate_continuous(self):
        s_id = "EC228"

        study_frame = self.class_(s_id=s_id, studies_path=self.studies_path)
        valid = study_frame.validate_continuous()

        assert isinstance(valid, bool)


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])
