""" hdf5xltek.py
A HDF5 file which contains data for XLTEK EEG data.
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
import datetime
import pathlib
from typing import Any, Union

# Third-Party Packages #
from baseobjects import singlekwargdispatchmethod
from classversioning import VersionType, Version, TriNumberVersion
import h5py
from hdf5objects import HDF5Dataset
from hdf5objects.hdf5bases import HDF5Map, HDF5File
from hdf5objects.datasets import TimeSeriesDataset, TimeSeriesMap, Axis
from hdf5objects.fileobjects import HDF5EEG, HDF5EEGMap
import numpy as np

# Local Packages #


# Definitions #
# Classes #
class XLTEKDataMap(TimeSeriesMap):
    """A map for the data of an XLTEK file."""
    default_attribute_names = {"sample_rate": "Sampling Rate",
                               "n_samples": "total samples",
                               "c_axis": "c_axis",
                               "t_axis": "t_axis"}
    default_map_names = {"channel_axis": "channel indices",
                         "sample_axis": "samplestamp axis",
                         "time_axis": "timestamp axis"}


class XLTEKData(TimeSeriesDataset):
    """An HDF5 Dataset which is for holding XLTEK Data."""
    default_map: HDF5Map = XLTEKDataMap()
    # Todo: Fix writing sample rate to file.

    @property
    def sample_rate(self) -> float | h5py.Empty:
        """The sample rate of this timeseries."""
        return self.attributes["sample_rate"]

    @sample_rate.setter
    def sample_rate(self, value: int | float | None) -> None:
        self._sample_rate = value
        if self.time_axis is not None:
            self._time_axis.sample_rate = value
        self.attributes["sample_rate"] = value


# Assign Cyclic Definitions
XLTEKDataMap.default_type = XLTEKData


class HDF5XLTEKMap(HDF5EEGMap):
    """A map for HDF5XLTEK files."""
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
                    "entry_axis": HDF5Map(type_=Axis, shape=(0, 0), dtype='i', maxshape=(None, 4))}


class HDF5XLTEK(HDF5EEG):
    """A HDF5 file which contains data for XLTEK EEG data.

    Class Attributes:
        _registration: Determines if this class will be included in class registry.
        _VERSION_TYPE: The type of versioning to use.
        FILE_TYPE: The file type name of this class.
        VERSION: The version of this class.
        default_map: The HDF5 map of this object.

    Attributes:
        _entry_scale_name: The name of the entry scale axis.
        _entry_axis: The entry axis of this object.

    Args:
        file: Either the file object or the path to the file.
        s_id: The subject id.
        s_dir: The directory where subjects data are stored.
        start: The start time of the data, if creating.
        init: Determines if this object will construct.
        **kwargs: The keyword arguments for the open method.
    """
    _registration: bool = True
    _VERSION_TYPE: VersionType = VersionType(name="HDF5XLTEK", class_=TriNumberVersion)
    VERSION: Version = TriNumberVersion(0, 0, 0)
    FILE_TYPE: str = "XLTEK_EEG"
    default_map: HDF5Map = HDF5XLTEKMap()

    # File Validation
    @singlekwargdispatchmethod("file")
    @classmethod
    def validate_file_type(cls, file: pathlib.Path | str | HDF5File | h5py.File) -> bool:
        """Checks if the given file or path is a valid type.

        Args:
            file: The path or file object.

        Returns:
            If this is a valid file type.
        """
        raise TypeError(f"{type(file)} is not a valid type for validate_file_type.")

    @validate_file_type.register
    @classmethod
    def _(cls, file: pathlib.Path) -> bool:
        """Checks if the given path is a valid type.

        Args:
            file: The path.

        Returns:
            If this is a valid file type.
        """
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]

        if file.is_file():
            try:
                with h5py.File(file) as obj:
                    return start_name in obj.attrs and end_name in obj.attrs
            except OSError:
                return False
        else:
            return False

    @validate_file_type.register
    @classmethod
    def _(cls, file: str) -> bool:
        """Checks if the given path is a valid type.

        Args:
            file: The path.

        Returns:
            If this is a valid file type.
        """
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]

        file = pathlib.Path(file)

        if file.is_file():
            try:
                with h5py.File(file) as obj:
                    return start_name in obj.attrs and end_name in obj.attrs
            except OSError:
                return False
        else:
            return False

    @validate_file_type.register
    @classmethod
    def _(cls, file: HDF5File) -> bool:
        """Checks if the given file is a valid type.

        Args:
            file: The file object.

        Returns:
            If this is a valid file type.
        """
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]
        file = file._file
        return start_name in file.attrs and end_name in file.attrs

    @validate_file_type.register
    @classmethod
    def _(cls, file: h5py.File) -> bool:
        """Checks if the given file is a valid type.

        Args:
            file: The file object.

        Returns:
            If this is a valid file type.
        """
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]
        return start_name in file.attrs and end_name in file.attrs

    @singlekwargdispatchmethod("file")
    @classmethod
    def new_validated(cls, file: pathlib.Path | str | HDF5File | h5py.File, **kwargs: Any) -> Union["HDF5XLTEK", None]:
        """Checks if the given file or path is a valid type and returns the file if valid.

        Args:
            file: The path or file object.

        Returns:
            The file or None.
        """
        raise TypeError(f"{type(file)} is not a valid type for new_validate.")

    @new_validated.register
    @classmethod
    def _(cls, file: pathlib.Path, **kwargs: Any) -> Any:
        """Checks if the given path is a valid type and returns the file if valid.

        Args:
            file: The path.

        Returns:
            The file or None.
        """
        start_name = cls.default_map.attribute_names["start"]

        if file.is_file():
            try:
                file = h5py.File(file)
                if start_name in file.attrs:
                    return cls(file=file, **kwargs)
            except OSError:
                return None
        else:
            return None

    @new_validated.register
    @classmethod
    def _(cls, file: str, **kwargs: Any) -> Any:
        """Checks if the given path is a valid type and returns the file if valid.

        Args:
            file: The path.

        Returns:
            The file or None.
        """
        start_name = cls.default_map.attribute_names["start"]
        file = pathlib.Path(file)

        if file.is_file():
            try:
                file = h5py.File(file)
                if start_name in file.attrs:
                    return cls(obj=file, **kwargs)
            except OSError:
                return None
        else:
            return None

    @new_validated.register
    @classmethod
    def _(cls, file: HDF5File, **kwargs: Any) -> Any:
        """Checks if the given file is a valid type and returns the file if valid.

        Args:
            file: The file.

        Returns:
            The file or None.
        """
        start_name = cls.default_map.attribute_names["start"]
        file = file._file
        if start_name in file.attrs:
            return cls(file=file, **kwargs)
        else:
            return None

    @new_validated.register
    @classmethod
    def _(cls, file: h5py.File, **kwargs: Any) -> Any:
        """Checks if the given file is a valid type and returns the file if valid.

        Args:
            file: The file.

        Returns:
            The file or None.
        """
        start_name = cls.default_map.attribute_names["start"]
        if start_name in file.attrs:
            return cls(obj=file, **kwargs)
        else:
            return None

    # Magic Methods #
    def __init__(
        self,
        file: str | pathlib.Path | h5py.File | None = None,
        s_id: str | None = None,
        s_dir: str | pathlib.Path | None = None,
        start: datetime.datetime | float | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # New Attributes #
        self._entry_scale_name: str = "entry axis"

        self.entry_axis: Axis | None = None

        # Object Construction #
        if init:
            self.construct(file=file, s_id=s_id, s_dir=s_dir, start=start, **kwargs)

    @property
    def start_entry(self) -> np.ndarray:
        """The start entry of this file."""
        return self.attributes["start_entry"]

    @start_entry.setter
    def start_entry(self, value: tuple[int, int, int, int]) -> None:
        self.attributes.set_attribute("start_entry", value)

    @property
    def end_entry(self) -> np.ndarray:
        """The end entry of this file."""
        return self.attributes["end_entry"]

    @end_entry.setter
    def end_entry(self, value: tuple[int, int, int, int]) -> None:
        self.attributes.set_attribute("end_entry", value)

    @property
    def total_samples(self) -> int:
        """The total number of samples in this file."""
        return self.attributes["total_samples"]

    @total_samples.setter
    def total_samples(self, value: int) -> None:
        self.attributes.set_attribute("total_samples", value)
    
    # Instance Methods #
    # Constructors/Destructors
    def construct_file_attributes(
        self,
        start: datetime.datetime | float | None = None,
        map_: HDF5Map = None,
        load: bool = False,
        require: bool = False,
    ) -> None:
        """Creates the attributes for this group.

        Args:
            start: The start time of the data, if creating.
            map_: The map to use to create the attributes.
            load: Determines if this object will load the attribute values from the file on construction.
            require: Determines if this object will create and fill the attributes in the file on construction.
        """
        super().construct_file_attributes(start=start, map_=map_, load=load, require=require)
        if self.data.exists:
            self.attributes["total_samples"] = self.data.n_samples

    # Attributes Modification
    def standardize_attributes(self) -> None:
        """Sets the attributes that correspond to data the actual data values."""
        super().standardize_attributes()
        if self.data.exists:
            self.attributes["total_samples"] = self.data.n_samples

    # Entry Axis
    def create_entry_axis(self, axis: int | None = None, **kwargs: Any) -> Axis:
        """Creates the entry axis.

        Args:
            axis: The axis along which to attach this axis.
            **kwargs: Keyword arguments to create this Axis.
        """
        if axis is None:
            axis = self["data"].t_axis

        entry_axis = self.map["entry_axis"].type(file=self, dtype='i', maxshape=(None, 4), **kwargs)
        self.attach_entry_axis(entry_axis, axis)
        return self.entry_axis

    def attach_entry_axis(self, dataset: h5py.Dataset | HDF5Dataset, axis: int | None = None) -> None:
        """Attaches an axis (scale) to this file.

        Args:
            dataset: The dataset to attach as an axis (scale).
            axis: The axis to attach the axis (scale) to.
        """
        if axis is None:
            axis = self["data"].t_axis
        self["data"].attach_axis(dataset, axis)
        self.entry_axis = dataset
        self.entry_axis.make_scale(self._entry_scale_name)

    def detach_entry_axis(self, axis: int | None = None) -> None:
        """Detaches an axis (scale) from this dataset.

        Args:
            axis: The axis to detach the axis (scale) from.
        """
        if axis is None:
            axis = self.data.t_axis
        self.data.detach_axis(self.entry_axis, axis)
        self.entry_axis = None

    def load_entry_axis(self) -> None:
        """Loads the entry axis from the file"""
        with self.temp_open():
            if "entry axis" in self["data"].dims[self["data"].t_axis]:
                entry_axis = self["data"].dims[self["data"].t_axis]
                self.entry_axis = self.map["entry_axis"].type(
                    dataset=entry_axis,
                    s_name=self._entry_scale_name,
                    file=self,
                )

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
