"""xltekhdf5.py
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
from decimal import Decimal
from typing import Any
from typing import Union

# Third-Party Packages #
import h5py
import numpy as np

# Third-Party Packages #
from baseobjects.functions import singlekwargdispatch
from classversioning import TriNumberVersion
from classversioning import Version
from hdf5objects import HDF5Dataset
from hdf5objects.dataset import AxisMap
from hdf5objects.dataset import BaseTimeSeriesMap
from hdf5objects.dataset import ChannelAxisMap
from hdf5objects.dataset import SampleAxisMap
from hdf5objects.dataset import TimeAxisMap
from hdf5objects.dataset import TimeSeriesComponent
from hdf5objects.fileobjects import HDF5EEGMap
from hdf5objects.hdf5bases import HDF5File
from hdf5objects.hdf5bases import HDF5Map

# Local Packages #
from .xltekhdf5 import XLTEKHDF5


# Definitions #
# Classes #
class XLTEKTimeComponent(TimeSeriesComponent):
    """An HDF5 Dataset which is for holding XLTEK Data."""

    @property
    def _sample_rate(self) -> Decimal | None:
        """The sample rate of this timeseries."""
        try:
            return Decimal(self.composite.attributes["sample_rate"])
        except TypeError:
            return None

    @_sample_rate.setter
    def _sample_rate(self, value: Decimal | int | float | None) -> None:
        if value is not None and not isinstance(value, Decimal):
            value = Decimal(value)
        self._sample_rate_ = value
        if self.time_axis is not None:
            self.time_axis.sample_rate = value
        self.composite.attributes["sample_rate"] = value


class XLTEKDataMap_0(BaseTimeSeriesMap):
    """A map for the data of an XLTEK file."""

    default_attribute_names = {
        "sample_rate": "Sampling Rate",
        "n_samples": "total samples",
        "c_axis": "c_axis",
        "t_axis": "t_axis",
    }
    default_axis_maps = [
        {"time axis": TimeAxisMap(), "sample axis": SampleAxisMap()},
        {"channel indices": ChannelAxisMap()},
    ]
    default_component_types = {"timeseries": (XLTEKTimeComponent, {"scale_name": "time axis"})}


class XLTEKHDF5Map_0(HDF5EEGMap):
    """A map for XLTEKHDF5 files."""

    default_attribute_names = {
        "file_type": "type",
        "file_version": "version",
        "subject_id": "name",
        "start": "start time",
        "end": "end time",
        "start_entry": "start entry",
        "end_entry": "end entry",
        "total_samples": "total samples",
    }
    default_map_names = {"data": "ECoG Array", "entry_axis": "entry vector"}
    default_maps = {
        "data": XLTEKDataMap_0(),
        "entry_axis": AxisMap(object_kwargs={"shape": (0, 0), "dtype": "i", "maxshape": (None, 4)}),
    }


class HDF5XLTEK_0(XLTEKHDF5):
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

    VERSION: Version = TriNumberVersion(0, 1, 0)
    FILE_TYPE: str = "XLTEK_EEG"
    default_map: HDF5Map = XLTEKHDF5Map_0()

    # File Validation
    @singlekwargdispatch("file")
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
    def _validate_file_type(cls, file: pathlib.Path) -> bool:
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
    def _validate_file_type(cls, file: str) -> bool:
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
    def _validate_file_type(cls, file: HDF5File) -> bool:
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
    def _validate_file_type(cls, file: h5py.File) -> bool:
        """Checks if the given file is a valid type.

        Args:
            file: The file object.

        Returns:
            If this is a valid file type.
        """
        start_name = cls.default_map.attribute_names["start"]
        end_name = cls.default_map.attribute_names["end"]
        return start_name in file.attrs and end_name in file.attrs

    @singlekwargdispatch("file")
    @classmethod
    def new_validated(cls, file: pathlib.Path | str | HDF5File | h5py.File, **kwargs: Any) -> Union["XLTEKHDF5", None]:
        """Checks if the given file or path is a valid type and returns the file if valid.

        Args:
            file: The path or file object.

        Returns:
            The file or None.
        """
        raise TypeError(f"{type(file)} is not a valid type for new_validate.")

    @new_validated.register
    @classmethod
    def _new_validated(cls, file: pathlib.Path, **kwargs: Any) -> Any:
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
    def _new_validated(cls, file: str, **kwargs: Any) -> Any:
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
    def _new_validated(cls, file: HDF5File, **kwargs: Any) -> Any:
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
    def _new_validated(cls, file: h5py.File, **kwargs: Any) -> Any:
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

        self.entry_axis: HDF5Dataset | None = None

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
    def create_entry_axis(self, axis: int | None = None, **kwargs: Any) -> HDF5Dataset:
        """Creates the entry axis.

        Args:
            axis: The axis along which to attach this axis.
            **kwargs: Keyword arguments to create this Axis.
        """
        if axis is None:
            axis = self["data"].t_axis

        entry_axis = self.map["entry_axis"].type(file=self, dtype="i", maxshape=(None, 4), **kwargs)
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
