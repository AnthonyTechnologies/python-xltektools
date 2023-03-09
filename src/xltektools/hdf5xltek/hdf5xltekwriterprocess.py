""" hdf5xltekwriterprocess.py

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
from collections.abc import Iterable
import datetime
from multiprocessing import Process, Event, Queue
from queue import Empty
from typing import Any
from warnings import warn

# Third-Party Packages #
from hdf5objects import HDF5Dataset
import numpy as np

# Local Packages #


# Definitions #
# Functions #
def set_data(dataset: HDF5Dataset, data: np.ndrray, nanostamps: np.ndarray) -> None:
    dataset.set_data(data, component_kwargs={"timeseries": {"data": nanostamps}})


def append_data(dataset: HDF5Dataset, data: np.ndrray, nanostamps: np.ndarray) -> None:
    dataset.append(data, component_kwargs={"timeseries": {"data": nanostamps}})


def insert_data(
    dataset: HDF5Dataset,
    index: int,
    data: np.ndarray,
    nanostamps: np.ndarray,
) -> None:
    dataset.insert_data(index=index, data=data)
    dataset.components["timeseries"].time_axis.insert_data(index=index, data=nanostamps)


# Classes #
class HDF5XLTEKWriterProcess(Process):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    _operation_register = {"set": set_data, "append": append_data, "insert": insert_data}

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        file_type: type,
        file_kwargs: dict[str, Any],
        tzinfo: datetime.tzinfo,
        sample_rate: float,
        data_queue: Queue,
        alive_event: Event,
        writing_event: Event,
    ) -> None:
        # New Attributes #
        self._alive_event: Event = alive_event
        self._writing_event: Event = writing_event

        self._file_type: type = file_type
        self._file_kwargs: dict[str, Any] = file_kwargs
        self._tzinfo: datetime.tzinfo = tzinfo
        self._sample_rate: float = sample_rate

        self._data_queue: Queue = data_queue

        # Parent Attributes #
        super().__init__()

    # Instance Methods #
    # Process
    def run(self) -> None:

        with self._file_type(**self._file_kwargs) as f_object:
            f_object.time_axis.components["axis"].set_time_zone(self._tzinfo)
            f_object.time_axis.components["axis"].sample_rate = self._sample_rate
            f_object.swmr_mode = True
            dataset = f_object.data
            while self._alive_event.is_set():
                try:
                    write_information = self._data_queue.get(block=False)._asdict()
                except Empty:
                    pass
                else:
                    self._writing_event.set()

                    operation_name = write_information.pop("operation")
                    write_operation = self._operation_register.get(operation_name, None)
                    if write_operation is None:
                        warn(f"{operation_name} is not a valid write operation.")
                    else:
                        write_operation(dataset, **write_information)

                    self._data_queue.task_done()
                    self._writing_event.clear()
