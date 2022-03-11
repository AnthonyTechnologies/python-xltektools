""" hdf5xltek.py
Description:
"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__

# Imports #
# Standard Libraries #
import pathlib
from functools import singledispatchmethod
from typing import Union

# Third-Party Packages #
from classversioning import VersionType, TriNumberVersion
import h5py

# Local Packages #
from ..datasets import TimeSeriesMap, Axis
from hdf5objects.hdf5bases.hdf5file import HDF5Map, HDF5File
from .hdf5eeg import HDF5EEG, HDF5EEGMap


# Definitions #
# Classes #
class XLTEKDataMap(TimeSeriesMap):
    default_attribute_names = {"sample_rate": "Sampling Rate",
                               "n_samples": "total samples",
                               "c_axis": "c_axis",
                               "t_axis": "t_axis"}
    default_map_names = {"channel_axis": "channel indices",
                         "sample_axis": "samplestamp axis",
                         "time_axis": "timestamp axis"}


class HDF5EXLTEKMap(HDF5EEGMap):
    default_attribute_names = {"file_type": "type",
                               "file_version": "version",
                               "subject_id": "name",
                               "start": "start time",
                               "end": "end time",
                               "start_entry": "start entry",
                               "end_entry": "end entry",
                               "total_samples": "total samples"}
    default_map_names = {"data": "ECoG Array",
                         "entry_axis": "entry vector"}
    default_maps = {"data": XLTEKDataMap(),
                    "entry_axis": HDF5Map(type_=Axis)}


class HDF5XLTEK(HDF5EEG):
    _registration = True
    _VERSION_TYPE = VersionType(name="HDF5XLTEK", class_=TriNumberVersion)
    VERSION = TriNumberVersion(0, 0, 0)
    FILE_TYPE = "XLTEK_EEG"
    default_map = HDF5EXLTEKMap()

    # File Validation
    @classmethod
    def validate_file_type(cls, obj):
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]

        if isinstance(obj, (str, pathlib.Path)):
            if not isinstance(obj, pathlib.Path):
                obj = pathlib.Path(obj)

            if obj.is_file():
                try:
                    with h5py.File(obj, mode='r') as obj:
                        return start_name in obj.attrs and end_name in obj.attrs
                except OSError:
                    return False
            else:
                return False
        elif isinstance(obj, HDF5File):
            obj = obj._file
            return start_name in obj.attrs and end_name in obj.attrs

    @singledispatchmethod
    @classmethod
    def new_validated(cls, obj, mode="r+", **kwargs):
        raise TypeError("A path or file object must be given")

    @new_validated.register(HDF5File)
    @classmethod
    def _new_validated(cls, obj: HDF5File, **kwargs):
        start_name = cls.default_map.attribute_names["start"]
        obj = obj._file
        if start_name in obj.attrs:
            return cls(file=obj, **kwargs)

    @new_validated.register(str)
    @new_validated.register(pathlib.Path)
    @classmethod
    def _new_validated(cls, obj: Union[str, pathlib.Path], mode="r+", **kwargs):
        start_name = cls.default_map.attribute_names["start"]

        if isinstance(obj, str):
            obj = pathlib.Path(obj)

        if obj.is_file():
            try:
                obj = h5py.File(obj, mode=mode)
                if start_name in obj.attrs:
                    return cls(file=obj, **kwargs)
            except OSError:
                return None
        else:
            return None
    
    # Magic Methods #
    def __init__(self, file=None, s_id=None, s_dir=None, start=None, init=True, **kwargs):
        super().__init__(init=False)
        self._entry_scale_name = "entry axis"

        self.entry_axis = None

        if init:
            self.construct(file=file, s_id=s_id, s_dir=s_dir, start=start, **kwargs)

    @property
    def start_entry(self):
        return self.attributes["start_entry"]

    @start_entry.setter
    def start_entry(self, value):
        self.attributes.set_attribute("start_entry", value)

    @property
    def end_entry(self):
        return self.attributes["end_entry"]

    @end_entry.setter
    def end_entry(self, value):
        self.attributes.set_attribute("end_entry", value)

    @property
    def total_samples(self):
        return self.attributes["total_samples"]

    @total_samples.setter
    def total_samples(self, value):
        self.attributes.set_attribute("total_samples", value)
    
    # Instance Methods #
    # Constructors/Destructors
    def construct_file_attributes(self, **kwargs):
        super().construct_file_attributes(**kwargs)
        if self.data.exists:
            self.attributes["total_samples"] = self.data.n_samples

    def standardize_attributes(self):
        super().standardize_attributes()
        if self.data.exists:
            self.attributes["total_samples"] = self.data.n_samples

    # Entry Axis
    def create_entry_axis(self, axis=None, **kwargs):
        if axis is None:
            axis = self["data"].t_axis

        entry_axis = self.map["entry_axis"](file=self, dtype='i', maxshape=(None, 4), **kwargs)
        self.attach_entry_axis(entry_axis, axis)
        return self.entry_axis

    def attach_entry_axis(self, dataset, axis=None):
        if axis is None:
            axis = self["data"].t_axis
        self["data"].attach_axis(dataset, axis)
        self.entry_axis = dataset
        self.entry_axis.make_scale(self._entry_scale_name)

    def detach_entry_axis(self, axis=None):
        if axis is None:
            axis = self.data.t_axis
        self.data.detach_axis(self.entry_axis, axis)
        self.entry_axis = None

    def load_entry_axis(self):
        with self.temp_open():
            if "entry axis" in self["data"].dims[self["data"].t_axis]:
                entry_axis = self["data"].dims[self["data"].t_axis]
                self.entry_axis = self.map["entry_axis"].type(dataset=entry_axis, s_name=self._entry_scale_name,
                                                              file=self)

    # XLTEK Entry # Todo: Redesign this.
    # def format_entry(self, entry):
    #     data = entry["data"]
    #     n_channels = data.shape[self.data.c_axis]
    #     n_samples =data.shape[self._time_axis]
    #
    #     _channel_axis = np.arange(0, n_channels)
    #     _sample_axis = np.arrange(entry["start_sample"], entry["end_sample"])
    #
    #     entry_info = np.zeros((n_samples, 4), dtype=np.int32)
    #     entry_info[:, :] = entry["entry_info"]
    #
    #     _time_axis = np.zeros(n_samples, dtype=np.float64)
    #     for sample, i in enumerate(_sample_axis):
    #         delta_t = datetime.timedelta(seconds=((sample - entry["snc_sample"]) * 1.0 / entry['sample_rate']))
    #         time = entry["snc_time"] + delta_t
    #         _time_axis[i] = time.timestamp()
    #
    #     return data, _sample_axis, _time_axis, entry_info, _channel_axis, entry['sample_rate']
    #
    # def add_entry(self, entry):
    #     data, samples, times, entry_info, channels, sample_rate = self.format_entry(entry)
    #
    #     self.end_entry = entry_info[0]
    #     self.end = times[-1]
    #
    #     self.data.append_data(data)
    #     self._sample_axis.append(samples)
    #     self._time_axis.append(times)
    #     self.entry_axis.append(entry_info)
    #
    #     self.total_samples = self.data.n_samples
