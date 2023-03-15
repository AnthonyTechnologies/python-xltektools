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
from typing import Any, NamedTuple, Optional
from warnings import warn

# Third-Party Packages #
from hdf5objects import HDF5Dataset
import numpy as np

# Local Packages #


# Definitions #
# Functions #
def set_data(dataset: HDF5Dataset, data: np.ndarray, nanostamps: np.ndarray, **kwargs: Any) -> None:
    dataset.set_data(data, component_kwargs={"timeseries": {"data": nanostamps}})


def append_data(dataset: HDF5Dataset, data: np.ndarray, nanostamps: np.ndarray, **kwargs: Any) -> None:
    dataset.append(data, component_kwargs={"timeseries": {"data": nanostamps}})


def insert_data(
    dataset: HDF5Dataset,
    index: int,
    data: np.ndarray,
    nanostamps: np.ndarray,
    **kwargs: Any,
) -> None:
    dataset.insert_data(index=index, data=data)
    dataset.components["timeseries"].time_axis.insert_data(index=index, data=nanostamps)


# Classes #
class WriteFileItem(NamedTuple):
    kwargs: dict[str, Any]
    tzinfo: datetime.tzinfo
    sample_rate: float


class WriteDataItem(NamedTuple):
    operation: str
    index: int | None
    data: np.ndarray
    nanostamps: np.ndarray


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
        file_queue: Optional[Queue] = None,
        data_queue: Optional[Queue] = None,
        alive_event: Optional[Event] = None,
        writen_event: Optional[Event] = None,
    ) -> None:
        # New Attributes #
        self.alive_event: Event = Event() if alive_event is None else alive_event
        self.writen_event: Event = Event() if alive_event is None else writen_event

        self._file_type: type = file_type

        self.file_queue: Queue = Queue() if file_queue is None else file_queue
        self.data_queue: Queue = Queue() if data_queue is None else data_queue

        # Parent Attributes #
        super().__init__()

    # Instance Methods #
    # Process
    def run(self) -> None:
        while self.alive_event.is_set():
            try:
                file_info = self.file_queue.get_nowait()._asdict()
            except Empty:
                pass
            else:
                with self._file_type(**file_info["kwargs"]) as f_object:
                    f_object.time_axis.components["axis"].set_time_zone(file_info["tzinfo"])
                    f_object.time_axis.components["axis"].sample_rate = file_info["sample_rate"]
                    f_object.swmr_mode = True
                    dataset = f_object.data
                    while self.alive_event.is_set():
                        try:
                            item = self.data_queue.get_nowait()
                        except Empty:
                            pass
                        else:
                            if item is None:
                                break
                            else:
                                write_info = item._asdict()
                                operation_name = write_info.pop("operation")
                                write_operation = self._operation_register.get(operation_name, None)
                                if write_operation is None:
                                    warn(f"{operation_name} is not a valid write operation.")
                                else:
                                    write_operation(dataset, **write_info)

                                self.writen_event.set()
