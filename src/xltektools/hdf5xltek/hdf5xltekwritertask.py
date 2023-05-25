""" studyreadertask.py

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
from asyncio import sleep
from queue import Empty
from typing import Any, NamedTuple, Optional

# Third-Party Packages #
from dspobjects.time import Timestamp
from taskblocks import TaskBlock, AsyncEvent, AsyncQueueInterface, AsyncQueue, ArrayQueue, AsyncQueueManager

# Local Packages #
from .hdf5xltek import HDF5XLTEK


# Definitions #
# Classes #

class HDF5XLTEKWriterTask(TaskBlock):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    default_type = HDF5XLTEK.get_latest_version_class()

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        file_type: type | None = None,
        name: str = "",
        sets_up: bool = True,
        tears_down: bool = True,
        is_process: bool = False,
        s_kwargs: dict[str, Any] | None = None,
        t_kwargs: dict[str, Any] | None = None,
        d_kwargs: dict[str, Any] | None = None,
        *args: Any,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.file_type: type = self.default_type

        self.file = None
        self.file_kwargs: dict[str, Any] = {"file": ""}

        # Parent Attributes #
        super().__init__(*args, init=False, **kwargs)

        # Construct #
        if init:
            self.construct(
                file_type=file_type,
                name=name,
                sets_up=sets_up,
                tears_down=tears_down,
                is_process=is_process,
                s_kwargs=s_kwargs,
                t_kwargs=t_kwargs,
                d_kwargs=d_kwargs,
            )

    @property
    def write_queue(self) -> AsyncQueueInterface:
        """The queue manager to write data to."""
        return self.inputs.queues["write_queue"]

    @write_queue.setter
    def write_queue(self, value: AsyncQueueInterface) -> None:
        self.inputs.queues["write_queue"] = value

    @property
    def contents_info_queue(self) -> AsyncQueueInterface:
        """The queue to get studies from."""
        return self.outputs.queues["contents_info"]

    @contents_info_queue.setter
    def contents_info_queue(self, value: AsyncQueueInterface) -> None:
        self.outputs.queues["contents_info"] = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        file_type: type | None = None,
        name: str | None = None,
        sets_up: bool | None = None,
        tears_down: bool | None = None,
        is_process: bool | None = None,
        s_kwargs: dict[str, Any] | None = None,
        t_kwargs: dict[str, Any] | None = None,
        d_kwargs: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            file_type: The type of file to save the data as.
            name: Name of this object.
            sets_up: Determines if setup will be run.
            tears_down: Determines if teardown will be run.
            is_process: Determines if this task will run in another process.
            s_kwargs: Contains the keyword arguments to be used in the setup method.
            t_kwargs: Contains the keyword arguments to be used in the task method.
            d_kwargs: Contains the keyword arguments to be used in the teardown method.
            *args: Arguments for inheritance.
            **kwargs: Keyword arguments for inheritance.
        """
        if file_type is not None:
            self.file_type = file_type

        # Construct Parent #
        super().construct(
            name=name,
            sets_up=sets_up,
            tears_down=tears_down,
            is_process=is_process,
            s_kwargs=s_kwargs,
            t_kwargs=t_kwargs,
            d_kwargs=d_kwargs,
            *args,
            **kwargs,
        )

    # IO
    def construct_io(self) -> None:
        """Abstract method that constructs the io for this object."""
        self.inputs.queues["write_queue"] = ArrayQueue(bytes_wait=True, maxbytes=int(2e9))

        self.outputs.queues["contents_info"] = AsyncQueue()
        self.outputs.events["done"] = AsyncEvent()

    def link_inputs(self, *args: Any, **kwargs: Any) -> None:
        """Abstract method that gives a place to the inputs to other objects."""
        pass

    def link_outputs(self, *args: Any, **kwargs: Any) -> None:
        """Abstract method that gives a place to the outputs to other objects."""
        pass

    def link_io(self, *args: Any, **kwargs: Any) -> None:
        """Abstract method that gives a place to the io to other objects."""
        pass

    async def write_queue_get(self, interval: float = 0.0) -> Any:
        while self.loop_event.is_set():
            try:
                return self.write_queue.get(block=False)
            except Empty:
                if self.inputs.events["writing_done"].is_set():
                    self.loop_event.clear()
                    self.outputs.events["done"].set()
                    return None, None, None

                await sleep(interval)

    # Setup
    def setup(self, *args: Any, **kwargs: Any) -> None:
        """The method to run before executing task."""
        pass

    # TaskBlock
    async def task(self, *args: Any, **kwargs: Any) -> None:
        """The main method to execute."""
        data, nanostamps, info = await self.write_queue_get()
        if data is None:
            return

        file_kwargs = info.pop("file_kwargs")

        if file_kwargs["file"] != self.file_kwargs["file"]:
            if self.file is not None:
                self.file.close()

            try:
                self.file = self.file_type(**file_kwargs)
            except OSError:
                file_kwargs["file"].unlink(missing_ok=True)
                self.file = self.file_type(**file_kwargs)

            self.file.time_axis.components["axis"].set_time_zone(info["tzinfo"])
            self.file.time_axis.components["axis"].sample_rate = info["sample_rate"]
            self.file.swmr_mode = True

        dataset = self.file.data
        d_slicing = [slice(None, i) for i in data.shape]
        d_slicing[0] = slice(dataset.shape[0], data.shape[0])
        d_slicing = tuple(d_slicing)
        n_slicing = slice(self.file.time_axis.shape[0], data.shape[0])

        dataset.append(data[d_slicing], component_kwargs={"timeseries": {"data": nanostamps[n_slicing]}})
        dataset.flush()

        content_kwargs = info["contents_kwargs"]
        content_kwargs.update(
            start=Timestamp.fromnanostamp(nanostamps[0], tz=info["tzinfo"]),
            end=Timestamp.fromnanostamp(nanostamps[-1], tz=info["tzinfo"]),
            min_shape=data.shape,
            max_shape=data.shape,
            sample_rate=info["sample_rate"],
        )
        del data, nanostamps
        await self.contents_info_queue.put_async(content_kwargs)

    # Teardown
    def teardown(self, *args: Any, **kwargs: Any) -> None:
        """The method to run after executing task."""
        if self.file is not None:
            self.file.close()
