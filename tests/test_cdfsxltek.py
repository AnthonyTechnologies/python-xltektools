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


# Imports #
# Standard Libraries #
import datetime
import cProfile
import io
import os
import pstats
import datetime
import pathlib
import timeit

# Third-Party Packages #
from classversioning import VersionType, TriNumberVersion, Version
from dspobjects.time import Timestamp
import pytest
import h5py
import numpy as np

# Local Packages #
from src.xltektools.cdfs.xltekcontentsfile import XLTEKContentsFile
from src.xltektools.cdfs.xltekcdfs import XLTEKCDFS


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


class TestHDF5XLTEK(ClassTest):
    _VERSION_TYPE: VersionType = VersionType(name="HDF5EEG", class_=TriNumberVersion)
    VERSION: Version = TriNumberVersion(0, 0, 0)
    class_ = XLTEKContentsFile
    studies_path = pathlib.Path("/common/xltek/subjects")
    load_path = pathlib.Path.cwd().joinpath("tests/pytest_cache/EC228_2020-09-21_14~53~19.h5")
    save_path = pathlib.Path.cwd().joinpath("tests/pytest_cache/")

    @pytest.fixture
    def load_file(self):
        return self.class_(file=self.load_path)

    def test_validate_file(self):
        assert self.class_.validate_file_type(self.load_path)

    @pytest.mark.parametrize("mode", ['r', 'r+', 'a'])
    def test_new_object(self, mode):
        with self.class_(file=self.load_path, mode=mode) as f_obj:
            assert f_obj is not None
        assert True

    @pytest.mark.parametrize("mode", ['r', 'r+', 'a'])
    def test_load_whole_file(self, mode):
        with self.class_(file=self.load_path, mode=mode, load=True) as f_obj:
            assert f_obj is not None
        assert True

    def test_load_fragment(self):
        f_obj = self.class_(file=self.load_path)
        data = f_obj["data"]
        f_obj.close()
        assert data is not None

    def test_load_from_property(self):
        f_obj = self.class_(file=self.load_path)
        data = f_obj.data
        f_obj.close()
        assert data is not None

    def test_get_attribute(self):
        f_obj = self.class_(file=self.load_path)
        attribute = f_obj.attributes["start"]
        f_obj.close()
        assert attribute is not None

    def test_get_attribute_property(self):
        f_obj = self.class_(file=self.load_path)
        attribute = f_obj.start
        f_obj.close()
        assert attribute is not None

    def test_get_data(self):
        f_obj = self.class_(file=self.load_path)
        data = f_obj.data[0:1]
        f_obj.close()
        assert data.shape is not None

    def test_get_times(self):
        f_obj = self.class_(file=self.load_path)
        start = f_obj.time_axis.start_datetime
        f_obj.close()
        assert start is not None

    @pytest.mark.xfail
    def test_activate_swmr_mode(self):
        f_obj = self.class_(file=self.load_path)
        f_obj.swmr_mode = True
        assert f_obj.swmr_mode
        f_obj.close()
        assert True

    def test_create_file_build_empty(self, tmpdir):
        start = datetime.datetime.now()
        f_obj = self.class_(s_id="EC_test", s_dir=tmpdir, start=start, create=True, mode="a", require=True)
        assert f_obj.is_open
        f_obj.close()
        assert True

    def test_require_file(self, tmpdir):
        sample_rate = 1024
        n_channels = 128
        n_samples = 2048
        path = self.studies_path / "EC212" / "contents.h5"
        f_obj = self.class_(path=path, mode="a", create=True, require=True)
        f_obj.close()
        assert True

    def test_build_study(self):
        subject_path = self.studies_path / "EC212"
        path = subject_path / "contents.h5"

        c_file = self.class_(path=path, mode="a", create=True, require=True)

        content_group = c_file["data_content"]
        for day_dir in subject_path.iterdir():
            if day_dir.is_dir():
                for file in day_dir.glob("*.h5"):
                    with h5py.File(file.as_posix()) as data_file:
                        start = Timestamp.fromtimestamp(data_file.attrs["start time"])
                        end = Timestamp.fromtimestamp(data_file.attrs["end time"])
                        length = data_file.attrs["total samples"]
                        min_shape = data_file["ECoG Array"].shape
                        max_shape = min_shape
                        sample_rate = data_file["ECoG Array"].attrs["Sampling Rate"]

                    content_group.components["xltek_data"].insert_entry(
                        path=file.name,
                        start=start,
                        end=end,
                        length=length,
                        min_shape=min_shape,
                        max_shape=max_shape,
                        sample_rate=sample_rate,
                        day_path=file.parts[-2],
                    )

        n_days = content_group["days"].shape[0]
        c_file.close()

        assert n_days == 6

    def test_init_study(self):
        subject_path = self.studies_path / "EC212"
        study = XLTEKCDFS(path=subject_path)
        lengths = study.data.lengths
        length = len(study.data)
        start = study.data.start_datetime
        assert True

    def test_init_study_per(self):
        subject_path = self.studies_path / "EC212"

        pr = cProfile.Profile()
        pr.enable()

        study = XLTEKCDFS(path=subject_path)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        assert True

    def test_find_data_range_time_full(self):
        subject_path = self.studies_path / "EC212"
        first = datetime.datetime(2020, 1, 28, 0, 00, 00)
        second = datetime.datetime(2020, 1, 28, 0, 10, 00)
        study = XLTEKCDFS(path=subject_path)

        pr = cProfile.Profile()
        pr.enable()

        data_object = study.data.find_data_range(first, second, approx=True)

        pr.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        assert data_object.data is not None


# Main #
if __name__ == '__main__':
    pytest.main(["-v", "-s"])

