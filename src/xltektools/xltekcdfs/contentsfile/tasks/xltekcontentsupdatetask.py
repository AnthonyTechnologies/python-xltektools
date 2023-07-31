"""xltekcontentsupdatetask.py

"""
# Package Header #
from ....header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from asyncio import sleep
from queue import Empty
from typing import Any, Iterable

# Third-Party Packages #
from taskblocks import AsyncEvent
from taskblocks import AsyncQueue
from taskblocks import AsyncQueueInterface
from taskblocks import TaskBlock

# Local Packages #
from ..files import XLTEKContentsFile


# Definitions #
# Classes #


class XLTEKContentsUpdateTask(TaskBlock):
    """

    Class Attributes:

    Attributes:

    Args:

    """
    default_update_keys: Iterable[str] = ("start_id",)

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        contents_file: XLTEKContentsFile | None = None,
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
        self.contents_file: XLTEKContentsFile | None = None
        self.was_open: bool = False
        self.update_keys: Iterable[str] = self.default_update_keys

        # Parent Attributes #
        super().__init__(*args, init=False, **kwargs)

        # Construct #
        if init:
            self.construct(
                contents_file=contents_file,
                name=name,
                sets_up=sets_up,
                tears_down=tears_down,
                is_process=is_process,
                s_kwargs=s_kwargs,
                t_kwargs=t_kwargs,
                d_kwargs=d_kwargs,
            )

    @property
    def contents_entry_queue(self) -> AsyncQueueInterface:
        """The queue to get studies from."""
        return self.inputs.queues["contents_entry"]

    @contents_entry_queue.setter
    def contents_entry_queue(self, value: AsyncQueueInterface) -> None:
        self.inputs.queues["contents_entry"] = value

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        contents_file: type | None = None,
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
            contents_file: The contents file to update.
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
        if contents_file is not None:
            self.contents_file = contents_file

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
        self.inputs.queues["contents_entry"] = AsyncQueue()
        self.inputs.events["entries_done"] = AsyncEvent()
        self.outputs.events["done"] = AsyncEvent()

    async def entry_queue_get(self, interval: float = 0.0) -> list[dict[str, Any]] | None:
        items = []
        while self.loop_event.is_set():
            try:
                items.append(self.contents_entry_queue.get(block=False))
            except Empty:
                if items:
                    return items
                elif self.inputs.events["entries_done"].is_set():
                    self.loop_event.clear()
                    self.outputs.events["done"].set()
                    return None
                else:
                    await sleep(interval)

    # Setup
    def setup(self, *args: Any, **kwargs: Any) -> None:
        """The method to run before executing task."""
        self.was_open = False

        if not self.contents_file.is_async:
            self.contents_file.close()
        else:
            self.was_open = True

        if not self.contents_file.is_open:
            self.contents_file.open(async_=True)
        else:
            self.was_open = True

    # TaskBlock
    async def task(self, *args: Any, **kwargs: Any) -> None:
        """The main method to execute."""
        entries = await self.entry_queue_get()
        if entries is None:
            return

        with self.contents_file.async_session_maker() as session:
            await self.contents_file.contents.update_entries_async(
                session=session,
                entries=entries,
                primary_keys=self.update_keys,
                begin=True,
            )

    # Teardown
    def teardown(self, *args: Any, **kwargs: Any) -> None:
        """The method to run after executing task."""
        if not self.was_open:
            self.contents_file.close()
