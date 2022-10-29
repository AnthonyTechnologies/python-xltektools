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
import pathlib
import timeit

# Third-Party Packages #
from classversioning import VersionType, TriNumberVersion, Version
import pytest
import numpy as np

# Local Packages #
from src.xltektools.hdf5framestructure import *


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
    class_ = HDF5XLTEK
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

    def test_create_file_build_data(self, tmpdir):
        sample_rate = 1024
        n_channels = 128
        n_samples = 2048
        data = np.random.rand(n_samples, n_channels)
        start = datetime.datetime.now()

        f_obj = self.class_(s_id="EC_test", s_dir=tmpdir, start=start, create=True, mode="a", require=True)

        dataset = f_obj.data
        dataset.require(data=data, sample_rate=sample_rate, start=start)
        dataset.sample_rate = 1024

        f_obj.close()
        assert True

    @pytest.mark.xfail
    def test_data_speed(self, load_file):
        def assignment():
            x = 10

        def get_data():
            x = load_file.eeg_data[:10000, :100]

        mean_new = timeit.timeit(get_data, number=self.timeit_runs) / self.timeit_runs * 1000000
        mean_old = timeit.timeit(assignment, number=self.timeit_runs) / self.timeit_runs * 1000000
        percent = (mean_new / mean_old) * 100

        print(f"\nNew speed {mean_new:.3f} μs took {percent:.3f}% of the time of the old function.")
        assert percent < self.speed_tolerance


# Main #
if __name__ == '__main__':
    pytest.main(["-v", "-s"])

