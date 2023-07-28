"""xltekcdfscontenttask.py

"""
# Package Header #
from ...header import *


# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__

# Imports #
# Standard Libraries #
from asyncio import sleep
from queue import Empty
from typing import Any
from typing import NamedTuple
from typing import Optional

# Third-Party Packages #
from dspobjects.time import Timestamp
from taskblocks import AsyncEvent
from taskblocks import AsyncQueue
from taskblocks import AsyncQueueInterface
from taskblocks import AsyncQueueManager
from taskblocks import TaskBlock

# Local Packages #
from ..xltekcdfs import XLTEKCDFS


# Definitions #
# Classes #


class XLTEKCDFSContentTask(TaskBlock):
    """

    Class Attributes:

    Attributes:

    Args:

    """

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        cdfs: XLTEKCDFS | None = None,
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
        self.cdfs: XLTEKCDFS | None = None

        # Parent Attributes #
        super().__init__(*args, init=False, **kwargs)

        # Construct #
        if init:
            self.construct(
                cdfs=cdfs,
                name=name,
                sets_up=sets_up,
                tears_down=tears_down,
                is_process=is_process,
                s_kwargs=s_kwargs,
                t_kwargs=t_kwargs,
                d_kwargs=d_kwargs,
            )

    @property
    def contents_info_queue(self) -> AsyncQueueInterface:
        """The queue to get studies from."""
        return self.inputs.queues["contents_info"]

    @contents_info_queue.setter
    def contents_info_queue(self, value: AsyncQueueInterface) -> None:
        self.inputs.queues["contents_info"] = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        cdfs: type | None = None,
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
            file_type: The study manager to get the studies from.
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
        if cdfs is not None:
            self.cdfs = cdfs

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
        self.inputs.queues["contents_info"] = AsyncQueue()
        self.outputs.events["done"] = AsyncEvent()

    async def info_queue_get(self, interval: float = 0.0) -> Any:
        while self.loop_event.is_set():
            try:
                return self.contents_info_queue.get(block=False)
            except Empty:
                if self.inputs.events["info_done"].is_set():
                    self.loop_event.clear()
                    self.outputs.events["done"].set()
                    return None

                await sleep(interval)

    # Setup
    def setup(self, *args: Any, **kwargs: Any) -> None:
        """The method to run before executing task."""
        if self.cdfs.mode == "r":
            self.cdfs.close()

        if not self.cdfs:
            self.cdfs.open(mode="a", build=True, load=False)

    # TaskBlock
    async def task(self, *args: Any, **kwargs: Any) -> None:
        """The main method to execute."""
        content_info = await self.info_queue_get()
        if content_info is None:
            return

        entry = self.cdfs.contents_root_node.get_recursive_entry_start(
            content_info["start"],
            approx=False,
            tails=False,
            default=None,
        )
        if entry is None:
            self.cdfs.contents_root_node.insert_recursive_entry(**content_info)
        elif entry["End"] < content_info["end"]:
            self.cdfs.contents_root_node.set_recursive_entry(**content_info)

        self.cdfs.contents_file.flush()

    # Teardown
    def teardown(self, *args: Any, **kwargs: Any) -> None:
        """The method to run after executing task."""
        self.cdfs.close()
