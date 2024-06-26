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
from pathlib import Path
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
from ucsfbids.datasets import Dataset
from ucsfbids.datasets.importers.pia import DatasetPiaImporter
from pyedflib.highlevel import make_signal_headers, make_header, write_edf, read_edf
import matplotlib.pyplot as plt

# Local Packages #
from src.xltektools.xltekhdf5.xltekhdf5_0 import HDF5XLTEK_0
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
    subject_root = pathlib.Path("/data_store2/imaging/subjects")
    path_kleen = pathlib.Path("/scratch/anthonyfong/ucsfbids")
    out_path_kleen = pathlib.Path("/scratch/anthonyfong/bidstest")

    convert_subjects = (
        "EC300",
        "EC303",
    )

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
        subject = Subject(name="EC0212", parent_path=self.path_kleen, mode="r")

        exporter = subject.create_exporter("BIDS")
        exporter.execute_export(self.out_path_kleen, name="UPenn0000")

    def test_annotation_read(self):
        path = self.out_path_kleen / f"UPenn0000_task-day1.edf"
        sigs, sig_headers, header = read_edf(path.as_posix())
        assert header["annotations"]

    def test_old_data_first(self):
        secs = 30
        first = pathlib.Path("/userdata/afong/EpilepsySpikeDetection/EC212/EC212 2020-01-28 0-1.h5")
        old_file = HDF5XLTEK_0(first, mode="r")
        old_channel = old_file.data[512:512*(secs+1), 0] * -1

        start = datetime.datetime(1970, 1, 6, 0, 0, tzinfo=datetime.timezone.utc)
        stop = datetime.datetime(1970, 1, 6, 0, 1, tzinfo=datetime.timezone.utc)

        bids_subject = Subject(name="EC0212", parent_path=self.server_path)
        session = bids_subject.sessions["clinicalintracranial"]
        cdfs = session.modalities["ieeg"].require_cdfs(load=True)

        data = cdfs.data.find_data_slice(start, stop, approx=True)
        new_channel = data[0].data[1024:1024*(secs+1), 0]

        t_512 = np.arange(0, secs, 1 / 512)
        t_1024 = np.arange(0, secs, 1 / 1024)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='Old Data Blue, New Data Orange')
        ax.plot(t_512, old_channel)
        ax.plot(t_1024, new_channel)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='Old Data')
        ax.plot(t_512, old_channel)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='New Data')
        ax.plot(t_1024, new_channel)

    def test_old_data_more(self):
        secs = 30
        s_sec = 3570
        first = pathlib.Path("/userdata/afong/EpilepsySpikeDetection/EC212/EC212 2020-01-28 0-1.h5")
        old_file = HDF5XLTEK_0(first, mode="r")
        old_channel = old_file.data[512 * s_sec:512 * (secs + s_sec), 0] * -1

        start = datetime.datetime(1970, 1, 6, 0, 0, tzinfo=datetime.timezone.utc)
        stop = datetime.datetime(1970, 1, 6, 1, 0, tzinfo=datetime.timezone.utc)

        bids_subject = Subject(name="EC0212", parent_path=self.server_path)
        session = bids_subject.sessions["clinicalintracranial"]
        cdfs = session.modalities["ieeg"].require_cdfs(load=True)

        data = cdfs.data.find_data_slice(start, stop, approx=True)
        new_channel = data[0].data[1024 * s_sec:1024*(secs+s_sec), 0]
        data[0].time_axis.sample_rate

        t_512 = np.arange(0, secs, 1/512)
        t_1024 = np.arange(0, secs, 1 / 1024)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='Old Data Blue, New Data Orange')
        ax.plot(t_512, old_channel)
        ax.plot(t_1024, new_channel)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='Old Data')
        ax.plot(t_512, old_channel)

        fig, ax = plt.subplots()
        ax.set(xlabel='time (s)', ylabel='voltage (uV)', title='New Data')
        ax.plot(t_1024, new_channel)

        plt.show()

    def test_import_imaging(self):
        subjects = (f"EC{int(n[2:]):04d}" for n in self.convert_subjects)
        Dataset.default_importers["Pia"] = DatasetPiaImporter
        dataset = Dataset(
            path=self.server_path,
            mode="w",
            create=False,
            load=False,
        )
        dataset.create_importer("Pia", Path("/"), subjects=subjects).execute_import(
            source_patients=self.convert_subjects
        )

    def test_data_loading(self):
        # Import Package
        from xltektools.xltekucsfbids import IEEGXLTEK

        # Select Subject
        bids_subject = Subject(name="EC0212", parent_path=self.server_path)
        session = bids_subject.sessions["clinicalintracranial"]
        ieeg = session.modalities["ieeg"]
        cdfs = ieeg.require_cdfs()
        cdfs.open(mode="r", load=True)

        # Data
        data = cdfs.data

        # Times
        start = datetime.datetime(1970, 1, 6, 0, 0, tzinfo=datetime.timezone.utc)
        stop = datetime.datetime(1970, 1, 6, 0, 1, tzinfo=datetime.timezone.utc)

        #
        data, axis, start, end, start_index, send_index = data.find_data_slice(start, stop, approx=True)
        one_second_slice = data[0:1024, :]


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])
